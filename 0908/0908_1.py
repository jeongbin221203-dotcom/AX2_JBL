import streamlit as st
import pandas as pd
import numpy as np
import os

# ==============================================================================
# [반도체 수출 실적 분석 및 리포트 생성기]
# 실행 방법: streamlit run 0908_1.py
# ==============================================================================

# 페이지 기본 설정 (와이드 레이아웃, 대시보드 테마)
st.set_page_config(
    page_title="반도체 수출 데이터 분석 대시보드",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 헬퍼 함수: 샘플 데이터 생성 ---
def generate_sample_data(file_path):
    """실제 수출 실적과 유사한 그럴듯한 한국 무역 수출 샘플 데이터를 생성합니다."""
    np.random.seed(42)
    
    # 샘플 품목 및 HS코드 목록
    items = [
        {"HS코드": "854231", "품목명": "메모리 반도체 (DRAM)"},
        {"HS코드": "854232", "품목명": "시스템 반도체 (AP)"},
        {"HS코드": "854110", "품목명": "반도체 다이오드"},
        {"HS코드": "854239", "품목명": "기타 집적회로 반도체"},
        {"HS코드": "850440", "품목명": "정류기 및 전력 소자"},
        {"HS코드": "847130", "품목명": "휴대용 컴퓨터(노트북)"},
        {"HS코드": "851713", "품목명": "스마트폰용 무선통신기기"},
        {"HS코드": "852872", "품목명": "컬러 TV 수신기"},
        {"HS코드": "901380", "품목명": "액정표시장치 (LCD)"},
        {"HS코드": "847330", "품목명": "컴퓨터 부품 및 주변기기"}
    ]
    
    countries = ["미국", "베트남", "중국", "일본", "대만", "독일", "싱가포르", "멕시코"]
    
    data = []
    # 200개의 랜덤 수출 데이터 생성
    for _ in range(200):
        item = np.random.choice(items)
        country = np.random.choice(countries)
        
        # 수출 금액은 100달러 ~ 50,000달러 단위 (수출 실적이 없는 경우 0 또는 일부 마이너스 데이터도 포함)
        amount = np.random.randint(-1000, 150000)
        if amount < -500:
            amount = 0  # 마이너스는 0으로 처리하거나 제외 조건 테스트용
            
        data.append({
            "HS코드": item["HS코드"],
            "품목명": item["품목명"],
            "국가명": country,
            "수출금액": amount,
            "수출건수": np.random.randint(1, 100) if amount > 0 else 0,
            "기준월": np.random.choice(["2026-07", "2026-08", "2026-09"])
        })
        
    df_sample = pd.DataFrame(data)
    df_sample.to_csv(file_path, index=False, encoding='utf-8-sig')
    return df_sample


# --- 메인 대시보드 타이틀 ---
st.title("📊 반도체 수출 실적 데이터 분석 대시보드")
st.markdown("""
이 대시보드는 **HS코드가 85로 시작**하고 **반도체** 품목을 포함하며, **미국 또는 베트남**으로 실제 수출 실적(**수출금액 > 0**)이 있는 
데이터를 필터링하여 분석합니다. 최종 필터링된 **상위 10건의 수출 실적**을 출력하고 `report.csv` 파일로 자동 저장합니다.
""")
st.divider()

csv_filename = 'raw_trade_data.csv'

# CSV 파일 존재 여부 확인 및 자동 생성 안내
if not os.path.exists(csv_filename):
    with st.spinner("💾 'raw_trade_data.csv' 파일이 없어 테스트용 고품질 샘플 데이터를 자동으로 생성하고 있습니다..."):
        generate_sample_data(csv_filename)
    st.toast("💡 테스트용 'raw_trade_data.csv' 샘플 데이터를 성공적으로 생성했습니다!", icon="✅")

# 데이터 로드 (캐시 적용)
@st.cache_data(ttl=60)
def load_data(file_path):
    return pd.read_csv(file_path)

try:
    # 데이터 불러오기
    df_raw = load_data(csv_filename)
    
    # ------------------ 사이드바 (필터 컨트롤 및 정보) ------------------
    st.sidebar.image("https://img.icons8.com/clouds/150/000000/analytics.png", width=120)
    st.sidebar.header("🎯 조건 설정 및 필터링")
    st.sidebar.write("수출 실적 분석의 필터 조건을 실시간으로 설정할 수 있습니다. (기본값은 사용자 요구조건으로 고정되어 있습니다)")
    
    # 요구사항 조건 입력 (사이드바 제어로 인터랙티브함 제공)
    hs_prefix = st.sidebar.text_input("HS코드 시작값", "85")
    search_keyword = st.sidebar.text_input("품목명 검색 키워드", "반도체")
    target_countries = st.sidebar.multiselect("대상 국가", ["미국", "베트남", "중국", "일본", "대만"], default=["미국", "베트남"])
    min_amount = st.sidebar.number_input("최소 수출금액 초과 기준", min_value=0, value=0)
    
    # 파일 업로더 제공 (사용자가 원하면 직접 실제 데이터를 업로드하여 분석 가능)
    st.sidebar.divider()
    st.sidebar.subheader("📂 실제 데이터 올리기")
    uploaded_file = st.sidebar.file_uploader("직접 보유한 CSV 파일을 업로드하여 분석하세요.", type=["csv"])
    
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ 사용자 지정 파일이 성공적으로 업로드되었습니다!")
        
    # --- 데이터 전처리 ---
    # 복사본 생성
    df = df_raw.copy()
    
    # 컬럼명 유연성 확보 (사용자 CSV의 다양한 컬럼명에 대응 가능하도록 안전장치 구현)
    col_mapping = {
        'HS코드': ['HS코드', 'HS Code', 'hs코드', 'HS_코드', 'hs_code'],
        '품목명': ['품목명', '품목', 'Item', '품목이름', 'item_name'],
        '국가명': ['국가명', '국가', 'Country', '수출국', 'country_name'],
        '수출금액': ['수출금액', '수출액', '수출 금액', 'Amount', 'export_amount']
    }
    
    for standard_col, alternative_cols in col_mapping.items():
        if standard_col not in df.columns:
            for alt in alternative_cols:
                if alt in df.columns:
                    df.rename(columns={alt: standard_col}, inplace=True)
                    break
                    
    # 필수 컬럼 검사
    required_cols = ['HS코드', '품목명', '국가명', '수출금액']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"❌ 필수 컬럼이 데이터에 유실되었습니다: {missing_cols}")
        st.info("💡 CSV 파일 내에 [HS코드, 품목명, 국가명, 수출금액]에 해당하거나 유사한 컬럼이 있는지 확인해주세요.")
    else:
        # 데이터 타입 정제
        df['HS코드'] = df['HS코드'].astype(str).str.strip()
        df['품목명'] = df['품목명'].astype(str).str.strip()
        df['국가명'] = df['국가명'].astype(str).str.strip()
        df['수출금액'] = pd.to_numeric(df['수출금액'], errors='coerce').fillna(0)
        
        # 1. 다중 조건 설정 및 필터링
        condition = (
            (df['HS코드'].str.startswith(hs_prefix)) & 
            (df['품목명'].str.contains(search_keyword, na=False)) & 
            (df['국가명'].isin(target_countries)) & 
            (df['수출금액'] > min_amount)
        )
        
        filtered_df = df[condition]
        
        # 2. 수출금액 기준 내림차순 정렬 후 상위 10건 추출
        top10_df = filtered_df.sort_values(by='수출금액', ascending=False).head(10)
        
        # 3. 로컬 CSV 저장 (한글 깨짐 방지를 위해 UTF-8-BOM 인코딩 사용)
        report_file_path = 'report.csv'
        top10_df.to_csv(report_file_path, index=False, encoding='utf-8-sig')
        
        # --- UI 레이아웃 구성 ---
        
        # 메트릭 카드 영역 (전체 요약 통계)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="📁 원본 전체 데이터 수", 
                value=f"{len(df_raw):,} 건"
            )
        with col2:
            st.metric(
                label="🔍 필터 조건 일치 데이터 수", 
                value=f"{len(filtered_df):,} 건",
                delta=f"{len(filtered_df) - len(df_raw)}",
                delta_color="inverse"
            )
        with col3:
            total_export_sum = top10_df['수출금액'].sum()
            st.metric(
                label="💵 상위 10건 총 수출금액", 
                value=f"${total_export_sum:,.0f}"
            )
        with col4:
            avg_export = top10_df['수출금액'].mean() if len(top10_df) > 0 else 0
            st.metric(
                label="📈 상위 10건 평균 수출금액", 
                value=f"${avg_export:,.0f}"
            )
            
        st.write("")
        
        # 주요 콘텐츠 영역 (좌측 표 / 우측 시각화 차트)
        main_col1, main_col2 = st.columns([1.2, 1.0])
        
        with main_col1:
            st.subheader("📊 조건 필터링 수출실적 상위 10건 (report.csv)")
            if not top10_df.empty:
                # 데이터프레임 스타일 업그레이드
                st.dataframe(
                    top10_df.style.format({'수출금액': '${:,.0f}', '수출건수': '{:,.0f}'})
                    .background_gradient(subset=['수출금액'], cmap='Greens'),
                    use_container_width=True,
                    height=380
                )
                
                # 다운로드 버튼 추가
                csv_bytes = top10_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 필터링 리포트(report.csv) 웹 다운로드",
                    data=csv_bytes,
                    file_name="report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 필터링 조건에 부합하는 데이터가 없습니다. 사이드바의 조건을 조정해보세요.")
                
        with main_col2:
            st.subheader("📈 상위 10건 수출금액 시각화 차트")
            if not top10_df.empty:
                # 품목별 및 국가별 시각화용 데이터 가공
                chart_data = top10_df[['품목명', '수출금액', '국가명']].copy()
                chart_data['품목명_국가'] = chart_data['품목명'] + " (" + chart_data['국가명'] + ")"
                chart_data = chart_data.set_index('품목명_국가')[['수출금액']]
                
                # 스트림릿 내장 바 차트 출력
                st.bar_chart(chart_data, color="#2ca02c", height=380)
            else:
                st.info("시각화할 데이터가 없습니다.")
                
        st.divider()
        
        # 서브 분석 테이블: 국가별 수출 요약 (미국 vs 베트남)
        st.subheader("🌎 대상 국가별 요약 (미국 vs 베트남)")
        country_summary = filtered_df.groupby('국가명').agg(
            전체수출건수=('수출금액', 'count'),
            총수출금액=('수출금액', 'sum'),
            평균수출금액=('수출금액', 'mean'),
            최대수출금액=('수출금액', 'max')
        ).reset_index()
        
        if not country_summary.empty:
            sc1, sc2 = st.columns([1, 1])
            with sc1:
                st.dataframe(
                    country_summary.style.format({
                        '총수출금액': '${:,.0f}',
                        '평균수출금액': '${:,.0f}',
                        '최대수출금액': '${:,.0f}'
                    }),
                    use_container_width=True
                )
            with sc2:
                # 파이 차트 또는 간소화된 수평 바 차트
                summary_chart = country_summary.set_index('국가명')[['총수출금액']]
                st.bar_chart(summary_chart, horizontal=True, color="#1f77b4")
        else:
            st.info("국가별 요약 데이터가 없습니다.")

        # 성공 알림 메시지
        st.success(f"🎉 성공: 조건 필터링 및 정렬이 완료되었습니다! 현재 디렉토리에 '{report_file_path}' 파일로 자동 저장되었습니다.")

except FileNotFoundError:
    st.error("❌ 오류: 'raw_trade_data.csv' 파일을 로드할 수 없습니다.")
except KeyError as e:
    st.error(f"❌ 오류: 데이터 내에 필요한 {e} 컬럼을 찾을 수 없습니다. 컬럼명을 확인해 주세요.")
except Exception as e:
    st.error(f"❌ 알 수 없는 오류 발생: {e}")

# 하단 푸터
st.caption("Developed by Gemini CLI • Streamlit Trade Analytics v1.0")
