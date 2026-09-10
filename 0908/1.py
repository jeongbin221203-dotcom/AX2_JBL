import streamlit as st

# ==============================================================================
# [구구단 계산기]
# 사용자가 선택한 단의 구구단을 출력하거나, 2단부터 9단까지 전체를 보여주는 앱입니다.
# 실행 방법: streamlit run 1.py
# ==============================================================================

# 페이지 설정
st.set_page_config(page_title="구구단 계산기", page_icon="🔢", layout="wide")

# 제목 및 설명
st.title("🔢 구구단 계산기")
st.caption("파이썬과 Streamlit을 활용하여 만든 간단한 구구단 출력 프로그램입니다.")

# 사이드바 설정
st.sidebar.header("⚙️ 옵션 선택")
mode = st.sidebar.radio("출력 모드", ["특정 단 출력", "전체 구구단(2-9단) 보기"])

if mode == "특정 단 출력":
    st.subheader("🎯 특정 단 출력하기")
    
    # 사용자로부터 숫자 입력 받기
    dan = st.number_input("확인하고 싶은 단을 입력하세요 (2~19)", min_value=2, max_value=19, value=2, step=1)
    
    st.info(f"### 💡 {dan}단 결과")
    
    # 보기 좋게 카드 형태로 출력하기 위해 columns 활용
    cols = st.columns(3)
    for i in range(1, 10):
        with cols[(i-1) % 3]:
            st.markdown(f"#### {dan} × {i} = `{dan * i}`")

else:
    st.subheader("📊 전체 구구단 (2단 ~ 9단)")
    
    # 2단부터 9단까지 4열로 배치
    for i in range(2, 10, 4): # 2, 6단부터 시작
        cols = st.columns(4)
        for j in range(4):
            current_dan = i + j
            if current_dan <= 9:
                with cols[j]:
                    st.success(f"**{current_dan}단**")
                    for k in range(1, 10):
                        st.text(f"{current_dan} × {k} = {current_dan * k}")
        st.write("---")

# 하단 정보
st.divider()
st.caption("© 2026 Gemini CLI Multiplication Table App")
