import os
from pathlib import Path
import folium
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium

# 1. 페이지 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="서울 주요 명소 지도", layout="wide")

# 2. 환경변수 로드
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

st.title("🗺️ 카카오 REST API 기반 서울 명소 지도")
st.caption("카카오 주소 검색 API로 좌표를 변환하여 Folium 지도에 표시합니다.")
st.divider()

if not KAKAO_REST_API_KEY:
    st.error("⚠️ `.env` 파일에 `KAKAO_REST_API_KEY`가 설정되어 있지 않습니다.")
    st.stop()


# 3. 카카오 주소 -> 좌표 변환 함수 (Streamlit 캐싱 적용)
@st.cache_data(show_spinner=False)
def get_coordinates(address: str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            documents = response.json().get("documents")
            if documents:
                lon = float(documents[0]["x"])
                lat = float(documents[0]["y"])
                return lat, lon
    except Exception as e:
        st.warning(f"'{address}' 좌표 변환 실패: {e}")
    return None


# 4. 주소 데이터셋
address_list = [
    {"name": "경복궁", "address": "서울특별시 종로구 사직로 161"},
    {"name": "서울시청", "address": "서울특별시 중구 세종대로 110"},
    {"name": "N서울타워", "address": "서울특별시 용산구 남산공원길 105"},
    {"name": "동대문디자인플라자(DDP)", "address": "서울특별시 중구 을지로 281"},
]

# 5. 좌표 변환 실행
valid_places = []
for item in address_list:
    coords = get_coordinates(item["address"])
    if coords:
        valid_places.append(
            {
                "name": item["name"],
                "address": item["address"],
                "lat": coords[0],
                "lon": coords[1],
            }
        )

# 6. 화면 레이아웃 (좌측: 명소 리스트 / 우측: Folium 지도)
col_info, col_map = st.columns([1, 2], gap="large")

with col_info:
    st.subheader("📍 등록된 장소 목록")
    for place in valid_places:
        with st.container(border=True):
            st.markdown(f"**{place['name']}**")
            st.caption(place["address"])
            st.caption(f"위도: `{place['lat']}` | 경도: `{place['lon']}`")

with col_map:
    if valid_places:
        center_lat = sum(p["lat"] for p in valid_places) / len(valid_places)
        center_lon = sum(p["lon"] for p in valid_places) / len(valid_places)

        # 워터마크가 없는 OpenStreetMap 기본 타일 적용
        map_obj = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles="OpenStreetMap"
        )

        for place in valid_places:
            folium.Marker(
                location=[place["lat"], place["lon"]],
                tooltip=place["name"],
                popup=folium.Popup(f"<b>{place['name']}</b><br>{place['address']}", max_width=250),
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(map_obj)

        st_folium(map_obj, width="100%", height=550, returned_objects=[])
    else:
        st.warning("표시할 수 있는 유효한 좌표 데이터가 없습니다.")