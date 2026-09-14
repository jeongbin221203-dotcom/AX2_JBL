import streamlit as st

# 1. 페이지 기본 설정 (브라우저 탭 타이틀 및 레이아웃)
st.set_page_config(
    page_title="글로벌 여행 포털",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 페이지 등록 (파일 경로, 제목, 이모지 아이콘)
home_page = st.Page("src/views/home.py", title="대한민국 (Home)", icon=":material/home:", default=True)
china_page = st.Page("src/views/china.py", title="중국", icon=":material/public:")
japan_page = st.Page("src/views/japan.py", title="일본", icon=":material/flight_takeoff:")
usa_page = st.Page("src/views/usa.py", title="미국", icon=":material/travel_explore:")

# 3. 사이드바 그룹 네비게이션 생성
pg = st.navigation(
    {
        "메인": [home_page],
        "해외 여행지": [china_page, japan_page, usa_page]
    }
)

# 4. 앱 실행
pg.run()