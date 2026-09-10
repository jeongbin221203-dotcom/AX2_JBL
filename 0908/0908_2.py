# raw_trade_data.csv 파일 활용
# HS코드가 85로 시작하는
# 반도체 + 국가명 미국 또는 베트남 + 수출금액 0보다 큰수 (실제 수출실적이 있는)
# 행만 다중 조건으로 필터링 한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv로 저장
# streamlit 사용 streamlit run 0908_1.py



import streamlit as st
import pandas as pd
import os

# 페이지 기본 설정 (가로로 넓게 사용)
st.set_page_config(page_title="무역 수출 데이터 분석", layout="wide")
st.title("반도체 수출 실적 분석 대시보드")

# 파일 경로 설정
csv_PATH = os.path.join(os.path.dirname(__file__), "..", "common", "raw_trade_data.csv")

@st.cache_data
def load_data():
    return pd.read_csv(csv_PATH, encoding='utf-8')

try:
    df = load_data()
    df['hs_code'] = df['hs_code'].astype(str)

    # ==========================================
    # 1. 사이드바 (옵션 설정 UI)
    # ==========================================
    st.sidebar.header("🔍 검색 필터 옵션")
    
    # 국가 목록을 데이터에서 동적으로 가져와 선택 옵션으로 제공
    country_list = df['국가명'].dropna().unique().tolist()
    default_countries = [c for c in ['미국', '베트남'] if c in country_list]
    selected_countries = st.sidebar.multiselect("국가 선택", country_list, default=default_countries)
    
    # 텍스트 및 숫자 입력 옵션
    hs_prefix = st.sidebar.text_input("HS코드 시작 번호", value="85")
    keyword = st.sidebar.text_input("품목명 키워드", value="반도체")
    top_n = st.sidebar.slider("출력할 상위 데이터 개수", min_value=5, max_value=30, value=10, step=5)

    # ==========================================
    # 2. 데이터 필터링 로직
    # ==========================================
    if selected_countries:
        condition = (
            (df['hs_code'].str.startswith(hs_prefix)) & 
            (df['품목명'].str.contains(keyword, na=False)) & 
            (df['국가명'].isin(selected_countries)) & 
            (df['수출금액'] > 0)
        )

        filtered_df = df[condition]
        top_df = filtered_df.sort_values(by='수출금액', ascending=False).head(top_n)

        # ==========================================
        # 3. 화면 출력 (표와 그래프를 좌우로 분할)
        # ==========================================
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📊 수출금액 상위 {top_n}건")
            st.dataframe(top_df, use_container_width=True)

        with col2:
            st.subheader("📈 날짜 및 국가별 수출금액 차트")
            if not top_df.empty:
                import plotly.express as px
                # barmode='group'을 통해 막대를 나란히 배치
                fig = px.bar(top_df, x='날짜', y='수출금액', color='국가명', barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("조건에 맞는 데이터가 없어 그래프를 그릴 수 없습니다.")

        # ==========================================
        # 4. 파일 저장 및 다운로드
        # ==========================================
        top_df.to_csv('report.csv', index=False, encoding='utf-8-sig')
        st.success(f"데이터 필터링 완료! 현재 폴더에 'report.csv' 파일이 저장되었습니다.")
        
    else:
        st.warning("👈 사이드바에서 국가를 최소 1개 이상 선택해주세요.")

except FileNotFoundError:
    st.error(f"오류: '{csv_PATH}' 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
except KeyError as e:
    st.error(f"오류: 데이터프레임에 {e} 컬럼이 없습니다. CSV 파일의 실제 컬럼명과 일치하는지 확인해주세요.")