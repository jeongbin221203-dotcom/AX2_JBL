import os
import streamlit as st
from PIL import Image, ImageOps

def get_cropped_image(image_path_or_url, size=(500, 400)):
    """이미지를 지정한 규격으로 중앙 크롭하여 반환"""
    try:
        if image_path_or_url.startswith("http"):
            import requests
            from io import BytesIO
            res = requests.get(image_path_or_url)
            img = Image.open(BytesIO(res.content))
        else:
            img = Image.open(image_path_or_url)
        
        # 비율을 유지하며 넘치는 부분을 중앙 기준으로 잘라냄
        return ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    except Exception:
        return None

def render_country_page(
    flag: str,
    country_name: str,
    subtitle: str,
    description: str,
    official_url: str,
    image_name: str = None
):
    st.title(f"{flag} {country_name}")
    st.caption(subtitle)
    st.divider()

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        if image_name:
            if image_name.startswith("http"):
                img = get_cropped_image(image_name, size=(500, 400))
            else:
                img_path = os.path.join(os.path.dirname(__file__), "..", "assets", image_name)
                img = get_cropped_image(img_path, size=(500, 400)) if os.path.exists(img_path) else None

            if img:
                st.image(img, caption=f"{country_name} 대표 풍경", use_container_width=True)
            else:
                st.info(f"📸 이미지가 준비되지 않았습니다. (`src/assets/{image_name}`)")
        else:
            st.info("📸 등록된 이미지가 없습니다.")

    with col2:
        st.subheader(f"📌 {country_name} 여행 정보")
        st.write(description)
        st.write("")
        st.link_button(
            label=f"🌐 {country_name} 공식 관광청 바로가기",
            url=official_url,
            type="primary",
            use_container_width=True
        )