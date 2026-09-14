import streamlit as st


# 페이지 전체 기본 설정
st.set_page_config(page_title="세계 여행 포털", page_icon="🌍", layout="centered")


home_page = st.Page("view/home.py", title="홈", icon="🏬", default=True)
usa_page = st.Page("view/usa.py", title="미국", icon="🇺🇸")
china_page = st.Page("view/china.py", title="중국", icon="🇨🇳")
japan_page = st.Page("view/japan.py", title="일본", icon="🇯🇵")
# 2. 네비게이션 메뉴 등록
pg = st.navigation([home_page, usa_page, china_page, japan_page])
# 3. 앱 실행
pg.run()



# # 1. 각 페이지 정의 (소문자 파일명 반영)
# home_page = st.Page("view/home.py", title="홈", icon="🗺️", default=True)
# usa_page = st.Page("view/usa.py", title="미국", icon="us")
# china_page = st.Page("view/china.py", title="중국", icon="cn")
# japan_page = st.Page("view/japan.py", title="일본", icon="jp")


