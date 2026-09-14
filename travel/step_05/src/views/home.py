import os
import streamlit as st
from PIL import Image, ImageOps

st.title("🏠 대한민국 (Korea)")
st.caption("세계 여행 포털에 오신 것을 환영합니다!")
st.divider()

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "korea.jpg")
    if os.path.exists(img_path):
        raw_img = Image.open(img_path)
        # 국가 페이지와 동일한 (500, 400) 규격 적용
        cropped_img = ImageOps.fit(raw_img, (500, 400), Image.Resampling.LANCZOS)
        st.image(cropped_img, caption="아름다운 대한민국", use_container_width=True)
    else:
        st.info("📸 `src/assets/korea.jpg` 이미지를 추가해주세요.")

with col2:
    st.markdown("""
    ### ✈️ 여행 안내
    사이드바 메뉴를 통해 관심 있는 국가의 정보와 공식 관광청 웹사이트를 확인하실 수 있습니다.

    * **🏮 중국**: 유구한 역사 유적과 광활한 대자연
    * **⛩️ 일본**: 전통과 현대의 조화, 미식과 온천
    * **🗽 미국**: 대도시와 웅장한 국립공원
    """)
    st.write("")
    st.link_button(
        label="🌐 대한민국 구석구석 (한국관광공사)",
        url="https://korean.visitkorea.or.kr",
        use_container_width=True
    )