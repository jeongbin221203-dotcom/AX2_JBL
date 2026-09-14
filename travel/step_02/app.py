import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍", layout="centered")

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본"])

if menu == "홈":
    st.title("🇰🇷 대한민국")
    st.write(
        "대한민국은 유구한 역사와 현대적인 IT 기술, K-컬처가 공존하는 매력적인 나라입니다. "
        "사계절의 뚜렷한 아름다움과 풍부한 먹거리를 즐길 수 있습니다."
    )

elif menu == "미국":
    st.title("🇺🇸 미국")
    st.write(
        "미국은 광활한 대자연부터 세계적인 대도시까지 다양한 경험을 제공하는 나라입니다. "
        "그랜드 캐니언, 뉴욕, 옐로스톤 등 전 세계 여행자들의 버킷리스트 명소가 가득합니다."
    )
    st.link_button("미국 공식 관광 사이트 방문", "https://www.gousa.or.kr")

elif menu == "중국":
    st.title("🇨🇳 중국")
    st.write(
        "중국은 방대한 대륙과 수천 년의 유구한 역사를 간직한 나라입니다. "
        "만리장성, 자금성 등 세계문화유산부터 상하이의 화려한 스카이라인까지 다채로운 매력을 지니고 있습니다."
    )
    # 한국어 공식 사이트 (중국주서울관광사무소) 연결
    st.link_button("중국 공식 관광 사이트 방문", "https://www.visitchina.or.kr")

elif menu == "일본":
    st.title("🇯🇵 일본")
    st.write(
        "일본은 전통적인 온천 문화와 현대적인 대중문화가 어우러진 가까운 이웃 나라입니다. "
        "도쿄, 오사카, 후쿠오카, 홋카이도 등 지역마다 특색 있는 미식과 풍경을 자랑합니다."
    )
    st.link_button("일본 공식 관광 사이트 방문", "https://www.japan.travel/ko/kr/")