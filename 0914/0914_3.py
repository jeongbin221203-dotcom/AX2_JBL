import math
import os
from datetime import datetime
from pathlib import Path
import folium
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# 1. 페이지 설정
st.set_page_config(page_title="서울 여행 가이드 & 스마트 루트 플래너", layout="wide")

# 2. 환경변수 및 Secrets 로드 (로컬 .env & 클라우드 Secrets 완벽 호환)
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"

# 로컬에 .env가 있을 때만 로드 (없어도 에러 내거나 멈추지 않음)
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)


def get_secret(key_name: str, fallback_key: str = None):
    """Streamlit Secrets 우선 조회 후, 로컬 파일 부재 시 os.getenv로 안전하게 조회"""
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
        if fallback_key and fallback_key in st.secrets:
            return st.secrets[fallback_key]
    except Exception:
        pass

    val = os.getenv(key_name)
    if not val and fallback_key:
        val = os.getenv(fallback_key)
    return val


KAKAO_KEY = get_secret("KAKAO_REST_API_KEY")
WEATHER_KEY = get_secret("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_secret("EXCHANGE_API_KEY", "EXCHANGE_RATE_API_KEY")

# 로컬과 클라우드 모두에서 키를 찾지 못한 경우에만 에러 출력
if not KAKAO_KEY:
    st.error(
        "⚠️ API 키가 설정되지 않았습니다.\n\n"
        "- **로컬 실행:** `.env` 파일에 키를 작성하세요.\n"
        "- **Streamlit Cloud:** 앱의 `Settings` ➡️ `Secrets`에 키를 등록하세요."
    )
    st.stop()

st.title("🧭 서울 여행 가이드 & 스마트 루트 플래너")
st.caption("실시간 날씨와 글로벌 환율, 테마별 60대 명소·맛집, 자차/대중교통 상세 경비 비교 및 실제 경로를 지원합니다.")
st.divider()


# 3. 유틸리티 및 계산 함수
def calculate_distance(lat1, lon1, lat2, lon2):
    r = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def calculate_fuel_cost(distance_km, fuel_price=1650, fuel_efficiency=11.0):
    if distance_km <= 0:
        return 0
    return round((distance_km / fuel_efficiency) * fuel_price)


def calculate_transit_fare(distance_km):
    base_fare = 1400
    if distance_km <= 10.0:
        return base_fare
    extra_units = math.ceil((distance_km - 10.0) / 5.0)
    return base_fare + (extra_units * 100)


# 4. 외부 API 연동 함수
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency: str = "USD"):
    if not EXCHANGE_KEY:
        return {}
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_KEY}/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data.get("conversion_rates", {})
    except Exception:
        pass
    return {}


@st.cache_data(ttl=1800)
def get_current_weather(city_name: str = "Seoul"):
    if not WEATHER_KEY:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": WEATHER_KEY, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=1800)
def get_weather_forecast(city_name: str = "Seoul"):
    if not WEATHER_KEY:
        return []
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city_name, "appid": WEATHER_KEY, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("list", [])[:6]
    except Exception:
        pass
    return []


def search_kakao_place(keyword: str):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_KEY}"}
    params = {"query": keyword, "size": 1}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents")
            if docs:
                item = docs[0]
                category_group = item.get("category_group_name", "")
                cat = "맛집/미식" if "음식점" in category_group or "카페" in category_group else "기타"
                return {
                    "name": item["place_name"],
                    "address": item["road_address_name"] or item["address_name"],
                    "lat": float(item["y"]),
                    "lon": float(item["x"]),
                    "category": cat,
                    "admission": 0,
                    "desc": f"검색 추가 ({item.get('category_name', '장소')})",
                }
    except Exception:
        pass
    return None


def get_kakao_car_directions(start_lat, start_lon, end_lat, end_lon):
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {"Authorization": f"KakaoAK {KAKAO_KEY}"}
    params = {
        "origin": f"{start_lon},{start_lat}",
        "destination": f"{end_lon},{end_lat}",
        "priority": "RECOMMEND",
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            routes = res.json().get("routes", [])
            if routes and routes[0].get("result_code") == 0:
                summary = routes[0]["summary"]
                path_coords = []
                for section in routes[0].get("sections", []):
                    for road in section.get("roads", []):
                        vertexes = road.get("vertexes", [])
                        for i in range(0, len(vertexes), 2):
                            path_coords.append([vertexes[i + 1], vertexes[i]])

                return {
                    "duration": round(summary["duration"] / 60),
                    "distance": round(summary["distance"] / 1000, 1),
                    "toll": summary.get("fare", {}).get("toll", 0),
                    "path": path_coords,
                }
    except Exception:
        pass
    return None


def search_nearby_attractions(center_lat, center_lon, radius=2500):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_KEY}"}
    params = {
        "category_group_code": "AT4",
        "x": str(center_lon),
        "y": str(center_lat),
        "radius": radius,
        "size": 3,
        "sort": "popularity",
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return [
                {
                    "name": item["place_name"],
                    "address": item["road_address_name"] or item["address_name"],
                    "lat": float(item["y"]),
                    "lon": float(item["x"]),
                    "url": item.get("place_url", ""),
                }
                for item in res.json().get("documents", [])
            ]
    except Exception:
        pass
    return []


# 5. 상단 정보 브리핑 (환율 및 날씨)
col_top_info1, col_top_info2 = st.columns([1.2, 1], gap="medium")

with col_top_info1:
    rates = get_exchange_rates("USD")
    st.markdown("##### 💱 실시간 글로벌 환율 (기준: 1 USD)")
    if rates:
        r1, r2, r3 = st.columns(3)
        r1.metric("🇰🇷 한국 (KRW)", f"{rates.get('KRW', 0):,.1f} ₩")
        r2.metric("🇯🇵 일본 (JPY)", f"{rates.get('JPY', 0):,.1f} ¥")
        r3.metric("🇪🇺 유럽 (EUR)", f"{rates.get('EUR', 0):,.2f} €")

        r4, r5, r6 = st.columns(3)
        r4.metric("🇨🇳 중국 (CNY)", f"{rates.get('CNY', 0):,.2f} ¥")
        r5.metric("🇹🇼 대만 (TWD)", f"{rates.get('TWD', 0):,.1f} NT$")
        r6.metric("🇭🇰 홍콩 (HKD)", f"{rates.get('HKD', 0):,.2f} HK$")

with col_top_info2:
    weather = get_current_weather("Seoul")
    if weather and "main" in weather:
        st.markdown(f"##### 🌤️ 서울 현지 날씨 ({weather['weather'][0]['description']})")
        w1, w2, w3 = st.columns(3)
        w1.metric("기온", f"{weather['main']['temp']:.1f} °C")
        w2.metric("습도", f"{weather['main']['humidity']} %")
        w3.metric("체감온도", f"{weather['main']['feels_like']:.1f} °C")

forecast = get_weather_forecast("Seoul")
if forecast:
    f_cols = st.columns(len(forecast))
    for idx, item in enumerate(forecast):
        with f_cols[idx]:
            with st.container(border=True):
                st.caption(datetime.fromtimestamp(item["dt"]).strftime("%H시"))
                st.image(f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}.png", width=36)
                st.markdown(f"**{item['main']['temp']:.0f}°C**")

st.divider()

# 6. 테마별 10곳씩 총 60곳 엄선 데이터셋
DATASET_VERSION = "v2.4_60_places"

theme_places_60 = [
    # --- [1] 궁궐/역사 (10곳) ---
    {"name": "경복궁", "category": "궁궐/역사", "address": "서울특별시 종로구 사직로 161", "lat": 37.5759, "lon": 126.9768, "admission": 3000, "desc": "조선 제일의 법궁 (한복 착용 무료)"},
    {"name": "창덕궁 및 후원", "category": "궁궐/역사", "address": "서울특별시 종로구 율곡로 99", "lat": 37.5796, "lon": 126.9910, "admission": 3000, "desc": "유네스코 세계문화유산"},
    {"name": "창경궁", "category": "궁궐/역사", "address": "서울특별시 종로구 창경궁로 185", "lat": 37.5788, "lon": 126.9948, "admission": 1000, "desc": "대온실과 야간 상시 개장"},
    {"name": "덕수궁", "category": "궁궐/역사", "address": "서울특별시 중구 세종대로 99", "lat": 37.5658, "lon": 126.9752, "admission": 1000, "desc": "석조전과 도심 속 돌담길"},
    {"name": "경희궁", "category": "궁궐/역사", "address": "서울특별시 종로구 새문안로 55", "lat": 37.5714, "lon": 126.9682, "admission": 0, "desc": "조선 후기 5대 궁궐 (무료)"},
    {"name": "종묘", "category": "궁궐/역사", "address": "서울특별시 종로구 종로 157", "lat": 37.5746, "lon": 126.9940, "admission": 1000, "desc": "조선 왕조 신주를 모신 사당"},
    {"name": "청와대", "category": "궁궐/역사", "address": "서울특별시 종로구 청와대로 1", "lat": 37.5866, "lon": 126.9748, "admission": 0, "desc": "역사적 대통령 집무실 개방 공간"},
    {"name": "서대문형무소역사관", "category": "궁궐/역사", "address": "서울특별시 서대문구 통일로 251", "lat": 37.5744, "lon": 126.9562, "admission": 3000, "desc": "일제강점기 독립운동의 역사"},
    {"name": "서울 암사동 유적", "category": "궁궐/역사", "address": "서울특별시 강동구 올림픽로 875", "lat": 37.5599, "lon": 127.1305, "admission": 500, "desc": "국내 최대 신석기 시대 유적지"},
    {"name": "사육신역사공원", "category": "궁궐/역사", "address": "서울특별시 동작구 노량진로 156", "lat": 37.5145, "lon": 126.9416, "admission": 0, "desc": "단종 복위를 꾀한 사육신의 묘역"},

    # --- [2] 전망/랜드마크 (10곳) ---
    {"name": "N서울타워", "category": "전망/랜드마크", "address": "서울특별시 용산구 남산공원길 105", "lat": 37.5511, "lon": 126.9879, "admission": 21000, "desc": "서울 전경을 관람할 수 있는 랜드마크"},
    {"name": "롯데월드타워 서울스카이", "category": "전망/랜드마크", "address": "서울특별시 송파구 올림픽로 300", "lat": 37.5126, "lon": 127.1025, "admission": 31000, "desc": "국내 최고 123층 초고층 전망대"},
    {"name": "63스퀘어 63아트", "category": "전망/랜드마크", "address": "서울특별시 영등포구 63로 50", "lat": 37.5197, "lon": 126.9402, "admission": 15000, "desc": "여의도 한강 조망 미술관"},
    {"name": "동대문디자인플라자(DDP)", "category": "전망/랜드마크", "address": "서울특별시 중구 을지로 281", "lat": 37.5668, "lon": 127.0095, "admission": 0, "desc": "자하 하디드의 미래지향적 비정형 건축"},
    {"name": "남산골한옥마을", "category": "전망/랜드마크", "address": "서울특별시 중구 퇴계로34길 28", "lat": 37.5592, "lon": 126.9939, "admission": 0, "desc": "남산 아래 전통 가옥과 한옥 정원"},
    {"name": "세빛섬", "category": "전망/랜드마크", "address": "서울특별시 서초구 올림픽대로 2085-14", "lat": 37.5118, "lon": 126.9942, "admission": 0, "desc": "한강 위의 수변 복합 문화 플로팅 아일랜드"},
    {"name": "응봉산 팔각정", "category": "전망/랜드마크", "address": "서울특별시 성동구 응봉동 산5-1", "lat": 37.5487, "lon": 127.0315, "admission": 0, "desc": "한강과 도심 도로가 펼쳐지는 대표 야경"},
    {"name": "낙산공원 전망대", "category": "전망/랜드마크", "address": "서울특별시 종로구 낙산길 41", "lat": 37.5807, "lon": 127.0076, "admission": 0, "desc": "한양도성 성곽길 파노라마 야경"},
    {"name": "북악팔각정", "category": "전망/랜드마크", "address": "서울특별시 종로구 북악산로 267", "lat": 37.6011, "lon": 126.9782, "admission": 0, "desc": "북악스카이웨이 드라이브 및 서울 조망"},
    {"name": "하늘공원 억새밭", "category": "전망/랜드마크", "address": "서울특별시 마포구 하늘공원로 95", "lat": 37.5681, "lon": 126.8851, "admission": 0, "desc": "가을 억새와 한강 노을 전망 명소"},

    # --- [3] 문화/전시 (10곳) ---
    {"name": "국립중앙박물관", "category": "문화/전시", "address": "서울특별시 용산구 서빙고로 137", "lat": 37.5240, "lon": 126.9803, "admission": 0, "desc": "대한민국 대표 국립 박물관 (상설전 무료)"},
    {"name": "국립현대미술관 서울", "category": "문화/전시", "address": "서울특별시 종로구 삼청로 30", "lat": 37.5785, "lon": 126.9802, "admission": 5000, "desc": "도심 속 복합 현대미술 전시 공간"},
    {"name": "전쟁기념관", "category": "문화/전시", "address": "서울특별시 용산구 이태원로 29", "lat": 37.5366, "lon": 126.9772, "admission": 0, "desc": "야외 대형 군사장비 및 전쟁 역사 전시"},
    {"name": "서울시립미술관 본관", "category": "문화/전시", "address": "서울특별시 중구 덕수궁길 61", "lat": 37.5641, "lon": 126.9738, "admission": 0, "desc": "근대 건축미와 현대미술 기획전시"},
    {"name": "대한민국역사박물관", "category": "문화/전시", "address": "서울특별시 종로구 세종대로 198", "lat": 37.5739, "lon": 126.9783, "admission": 0, "desc": "광화문 앞 대한민국 근현대사 박물관"},
    {"name": "국립민속박물관", "category": "문화/전시", "address": "서울특별시 종로구 삼청로 37", "lat": 37.5816, "lon": 126.9790, "admission": 0, "desc": "선조들의 일상생활과 민속문화 전시"},
    {"name": "한성백제박물관", "category": "문화/전시", "address": "서울특별시 송파구 위례성대로 71", "lat": 37.5168, "lon": 127.1205, "admission": 0, "desc": "백제 한성기의 500년 도읍사 전시"},
    {"name": "예술의전당 한가람미술관", "category": "문화/전시", "address": "서울특별시 서초구 남부순환로 2406", "lat": 37.4789, "lon": 127.0118, "admission": 15000, "desc": "국내외 거장 블록버스터 기획 전시"},
    {"name": "세종문화회관", "category": "문화/전시", "address": "서울특별시 종로구 세종대로 175", "lat": 37.5724, "lon": 126.9756, "admission": 0, "desc": "세종 이야기·충무공 이야기 전시관"},
    {"name": "리움미술관", "category": "문화/전시", "address": "서울특별시 용산구 이태원로55길 60-16", "lat": 37.5385, "lon": 126.9995, "admission": 0, "desc": "고미술과 현대미술 상설전 (예약제 무료)"},

    # --- [4] 골목/쇼핑 (10곳) ---
    {"name": "북촌한옥마을", "category": "골목/쇼핑", "address": "서울특별시 종로구 계동길 37", "lat": 37.5826, "lon": 126.9836, "admission": 0, "desc": "전통 한옥 주거지역 보존 골목"},
    {"name": "익선동 한옥거리", "category": "골목/쇼핑", "address": "서울특별시 종로구 수표로28길 28", "lat": 37.5742, "lon": 126.9898, "admission": 0, "desc": "개성 넘치는 디저트 카페와 공방 거리"},
    {"name": "인사동 쌈지길", "category": "골목/쇼핑", "address": "서울특별시 종로구 인사동길 44", "lat": 37.5743, "lon": 126.9849, "admission": 0, "desc": "전통 공예품과 갤러리 쇼핑 공간"},
    {"name": "광장시장", "category": "골목/쇼핑", "address": "서울특별시 종로구 창경궁로 88", "lat": 37.5701, "lon": 126.9997, "admission": 0, "desc": "빈대떡·육회 등 서울 대표 먹거리 야시장"},
    {"name": "명동거리", "category": "골목/쇼핑", "address": "서울특별시 중구 명동길 43", "lat": 37.5636, "lon": 126.9850, "admission": 0, "desc": "패션 뷰티 쇼핑 및 길거리 음식의 메카"},
    {"name": "동묘 벼룩시장", "category": "골목/쇼핑", "address": "서울특별시 종로구 난계로27길 84", "lat": 37.5732, "lon": 127.0165, "admission": 0, "desc": "레트로 빈티지 의류 및 골동품 시장"},
    {"name": "성수동 카페거리", "category": "골목/쇼핑", "address": "서울특별시 성동구 연무장길 35", "lat": 37.5445, "lon": 127.0560, "admission": 0, "desc": "트렌디한 팝업스토어와 감성 카페 거리"},
    {"name": "홍대 걷고싶은거리", "category": "골목/쇼핑", "address": "서울특별시 마포구 어울마당로 145", "lat": 37.5558, "lon": 126.9272, "admission": 0, "desc": "버스킹 문화와 젊음의 패션 거리"},
    {"name": "남대문시장", "category": "골목/쇼핑", "address": "서울특별시 중구 남대문시장4길 21", "lat": 37.5592, "lon": 126.9776, "admission": 0, "desc": "갈치조림 골목과 대한민국 최대 전통시장"},
    {"name": "더현대 서울", "category": "골목/쇼핑", "address": "서울특별시 영등포구 여의대로 108", "lat": 37.5259, "lon": 126.9284, "admission": 0, "desc": "실내 정원 사운즈 포레스트 복합 백화점"},

    # --- [5] 자연/공원 (10곳) ---
    {"name": "여의도 한강공원", "category": "자연/공원", "address": "서울특별시 영등포구 여의동로 330", "lat": 37.5284, "lon": 126.9328, "admission": 0, "desc": "물빛광장과 치맥 피크닉 명소"},
    {"name": "반포 한강공원", "category": "자연/공원", "address": "서울특별시 서초구 신반포로11길 40", "lat": 37.5097, "lon": 126.9953, "admission": 0, "desc": "달빛무지개분수와 잠수교 산책로"},
    {"name": "서울숲", "category": "자연/공원", "address": "서울특별시 성동구 뚝섬로 273", "lat": 37.5444, "lon": 127.0374, "admission": 0, "desc": "사슴 방사장과 거대한 도심 생태숲"},
    {"name": "뚝섬 한강공원", "category": "자연/공원", "address": "서울특별시 광진구 강변북로 139", "lat": 37.5312, "lon": 127.0667, "admission": 0, "desc": "윈드서핑장 및 수변 잔디광장"},
    {"name": "올림픽공원", "category": "자연/공원", "address": "서울특별시 송파구 올림픽로 424", "lat": 37.5207, "lon": 127.1215, "admission": 0, "desc": "나홀로나무와 몽촌토성 산책로"},
    {"name": "서울식물원", "category": "자연/공원", "address": "서울특별시 강서구 마곡동로 161", "lat": 37.5694, "lon": 126.8353, "admission": 5000, "desc": "열대 및 지중해 대형 온실 식물원"},
    {"name": "북서울꿈의숲", "category": "자연/공원", "address": "서울특별시 강북구 월계로 173", "lat": 37.6219, "lon": 127.0423, "admission": 0, "desc": "도봉산 조망 전망대와 대형 호수공원"},
    {"name": "보라매공원", "category": "자연/공원", "address": "서울특별시 동작구 여의대방로20길 33", "lat": 37.4932, "lon": 126.9205, "admission": 0, "desc": "공군사관학교 터에 조성된 생태공원"},
    {"name": "남산 야외식물원", "category": "자연/공원", "address": "서울특별시 용산구 이태원동 258-329", "lat": 37.5408, "lon": 126.9942, "admission": 0, "desc": "남산 자락 고즈넉한 야외 산책 정원"},
    {"name": "청계천 (청계광장)", "category": "자연/공원", "address": "서울특별시 중구 태평로1가 1", "lat": 37.5694, "lon": 126.9778, "admission": 0, "desc": "서울 도심을 가로지르는 수변 산책로"},

    # --- [6] 맛집/미식 (10곳) ---
    {"name": "명동교자 본점", "category": "맛집/미식", "address": "서울특별시 중구 명동10길 29", "lat": 37.5626, "lon": 126.9856, "admission": 0, "desc": "미쉐린 빕 구르망 칼국수·만두 노포"},
    {"name": "우래옥 본점", "category": "맛집/미식", "address": "서울특별시 중구 창경궁로 62-29", "lat": 37.5682, "lon": 126.9987, "admission": 0, "desc": "진한 소고기 육향의 원조 평양냉면"},
    {"name": "토속촌 삼계탕", "category": "맛집/미식", "address": "서울특별시 종로구 자하문로5길 5", "lat": 37.5778, "lon": 126.9718, "admission": 0, "desc": "경복궁 옆 고소하고 진한 견과 삼계탕"},
    {"name": "을지면옥", "category": "맛집/미식", "address": "서울특별시 종로구 낙원동 288", "lat": 37.5736, "lon": 126.9882, "admission": 0, "desc": "의정부 계열의 담백한 평양냉면"},
    {"name": "필동면옥", "category": "맛집/미식", "address": "서울특별시 중구 서애로 26", "lat": 37.5601, "lon": 126.9972, "admission": 0, "desc": "고춧가루 살짝 띄운 감칠맛 냉면과 제육"},
    {"name": "이문설농탕", "category": "맛집/미식", "address": "서울특별시 종로구 우정국로 38-13", "lat": 37.5727, "lon": 126.9840, "admission": 0, "desc": "100년 넘는 역사의 대한민국 1호 음식점"},
    {"name": "백제정육점", "category": "맛집/미식", "address": "서울특별시 종로구 종로35길 34", "lat": 37.5714, "lon": 127.0042, "admission": 0, "desc": "종로 5가 가성비 최고의 육회·비빔밥"},
    {"name": "광장시장 순희네빈대떡", "category": "맛집/미식", "address": "서울특별시 종로구 종로32길 5", "lat": 37.5702, "lon": 127.0013, "admission": 0, "desc": "맷돌로 직접 간 녹두빈대떡과 고기완자"},
    {"name": "광화문 미진", "category": "맛집/미식", "address": "서울특별시 종로구 종로 19", "lat": 37.5709, "lon": 126.9798, "admission": 0, "desc": "진한 쯔유에 적셔먹는 판메밀의 명가"},
    {"name": "하동관 명동본점", "category": "맛집/미식", "address": "서울특별시 중구 명동9길 12", "lat": 37.5644, "lon": 126.9847, "admission": 0, "desc": "80년 전통 놋그릇에 담아내는 한우 곰탕"},
]

# 세션 캐시 충돌 방지를 위한 버전 검사 및 갱신
if "dataset_ver" not in st.session_state or st.session_state.dataset_ver != DATASET_VERSION:
    st.session_state.places = theme_places_60
    st.session_state.dataset_ver = DATASET_VERSION
else:
    existing_names = {p["name"] for p in st.session_state.places}
    for dp in theme_places_60:
        if dp["name"] not in existing_names:
            st.session_state.places.append(dp)

# 7. 상단 컨트롤 패널 (출발 위치 & 장소 검색)
c_loc, c_add = st.columns([1, 1], gap="medium")

with c_loc:
    loc_choice = st.radio("📍 출발 위치", ["실시간 기기 GPS", "주요 역 선택"], horizontal=True)
    cur_lat, cur_lon = 37.5663, 126.9779
    base_loc_label = "서울시청"

    if loc_choice == "실시간 기기 GPS":
        user_gps = get_geolocation()
        if user_gps and "coords" in user_gps:
            cur_lat = user_gps["coords"]["latitude"]
            cur_lon = user_gps["coords"]["longitude"]
            base_loc_label = "내 현재 위치"
            st.success(f"📡 위치 감지: `{cur_lat:.4f}, {cur_lon:.4f}`")
        else:
            st.info("💡 브라우저 상단에서 위치 권한을 허용해 주세요.")
    else:
        st_select = st.selectbox("출발 기준점", ["서울역", "강남역", "홍대입구역", "잠실역"])
        dict_pos = {
            "서울역": (37.5546, 126.9706),
            "강남역": (37.4979, 127.0276),
            "홍대입구역": (37.5575, 126.9244),
            "잠실역": (37.5133, 127.1001),
        }
        cur_lat, cur_lon = dict_pos[st_select]
        base_loc_label = st_select

with c_add:
    st.write("🔎 새로운 장소 찾기")
    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        new_place_query = st.text_input("새 장소", placeholder="장소명 입력 (예: 런던베이글뮤지엄)", label_visibility="collapsed")
    with s_col2:
        btn_add = st.button("목록 추가", use_container_width=True)

    if btn_add and new_place_query.strip():
        searched = search_kakao_place(new_place_query.strip())
        if searched:
            if not any(p["name"] == searched["name"] for p in st.session_state.places):
                st.session_state.places.append(searched)
                st.success(f"'{searched['name']}' 추가되었습니다.")
                st.rerun()
            else:
                st.warning("이미 목록에 있는 장소입니다.")
        else:
            st.error("장소를 찾지 못했습니다.")

# 기준점 기준 직선거리 계산 및 정렬
for p in st.session_state.places:
    p["dist"] = calculate_distance(cur_lat, cur_lon, p["lat"], p["lon"])
sorted_places = sorted(st.session_state.places, key=lambda x: x["dist"])

st.divider()

# 8. 메인 레이아웃: 좌측(목적지 선택) vs 우측(여정 브리핑 & 지도 & 환율 계산기)
col_nav, col_main = st.columns([1.1, 1.9], gap="large")

with col_nav:
    st.subheader("🎯 목적지 선택")

    categories = ["전체", "궁궐/역사", "전망/랜드마크", "문화/전시", "골목/쇼핑", "자연/공원", "맛집/미식"]
    if "cat_idx" not in st.session_state:
        st.session_state.cat_idx = 0

    st.markdown("##### 🏷️ 테마 필터")
    b_prev, b_label, b_next = st.columns([1, 4, 1])
    with b_prev:
        if st.button("◀", use_container_width=True):
            st.session_state.cat_idx = (st.session_state.cat_idx - 1) % len(categories)
            st.rerun()
    with b_label:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold; padding-top:6px; color:#2563EB; font-size:16px;'>{categories[st.session_state.cat_idx]}</div>",
            unsafe_allow_html=True,
        )
    with b_next:
        if st.button("▶", use_container_width=True):
            st.session_state.cat_idx = (st.session_state.cat_idx + 1) % len(categories)
            st.rerun()

    selected_cat = categories[st.session_state.cat_idx]

    filtered_places = (
        sorted_places
        if selected_cat == "전체"
        else [p for p in sorted_places if p.get("category") == selected_cat]
    )

    place_options = [p["name"] for p in filtered_places]
    if not place_options:
        st.info("해당 테마의 장소가 없습니다.")
        target_name = sorted_places[0]["name"]
    else:
        target_name = st.radio(
            "방문할 장소를 선택하세요",
            place_options,
            index=0,
            label_visibility="collapsed",
        )

    target_place = next(p for p in sorted_places if p["name"] == target_name)
    with st.container(border=True):
        st.markdown(f"### **{target_place['name']}**")
        st.caption(f"📍 {target_place.get('address', '')}")

        desc_text = target_place.get("desc") or target_place.get("admission_desc") or "서울 주요 명소"
        st.markdown(f"📝 {desc_text}")

        admission_val = target_place.get("admission", 0)
        cost_label = "입장료" if target_place.get("category") != "맛집/미식" else "입장료(식비별도)"
        admission_str = f"성인 {admission_val:,}원" if admission_val > 0 else "무료"
        st.markdown(
            f"**거리:** `{target_place.get('dist', 0):.2f} km`  |  **{cost_label}:** `{admission_str}`"
        )

with col_main:
    route_info = get_kakao_car_directions(cur_lat, cur_lon, target_place["lat"], target_place["lon"])
    linear_dist = target_place.get("dist", 0)
    driving_dist = route_info["distance"] if route_info else round(linear_dist * 1.3, 1)
    car_time = route_info["duration"] if route_info else round(linear_dist * 2.8) + 5
    toll_fare = route_info["toll"] if route_info else 0

    fuel_cost = calculate_fuel_cost(driving_dist)
    transit_fare = calculate_transit_fare(linear_dist)
    transit_time = max(round(linear_dist / 18 * 60) + 7, 10)
    admission_fee = target_place.get("admission", 0)

    with st.container(border=True):
        st.markdown(f"#### 🚗 여정 브리핑: `{base_loc_label}` ➡️ `{target_place['name']}`")

        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.markdown(f"**직선거리:** {linear_dist:.2f} km")
            st.markdown(f"**실제 주행거리:** {driving_dist} km")
        with info_col2:
            st.markdown(f"**🚗 자차 이동:** 약 **{car_time}분**")
            st.markdown(f"**🚌 대중교통:** 약 **{transit_time}분**")
        with info_col3:
            st.markdown(f"**자차 경비: 약 {(fuel_cost + toll_fare + admission_fee):,}원**")
            st.caption(f"주유비 {fuel_cost:,}원 + 통행료 {toll_fare:,}원 + 입장료 {admission_fee:,}원")
            st.markdown(f"**대중교통 경비: 약 {(transit_fare + admission_fee):,}원**")
            st.caption(f"교통카드 요금 {transit_fare:,}원 + 입장료 {admission_fee:,}원")

    mid_lat = (cur_lat + target_place["lat"]) / 2
    mid_lon = (cur_lon + target_place["lon"]) / 2
    waypoint_attractions = search_nearby_attractions(mid_lat, mid_lon, radius=2500)

    travel_map = folium.Map(location=[mid_lat, mid_lon], zoom_start=12, tiles="OpenStreetMap")

    # 출발지 마커
    folium.Marker(
        location=[cur_lat, cur_lon],
        tooltip=f"출발: {base_loc_label}",
        popup=f"<b>[출발] {base_loc_label}</b>",
        icon=folium.Icon(color="green", icon="user", prefix="fa"),
    ).add_to(travel_map)

    # 목적지 마커
    is_restaurant = target_place.get("category") == "맛집/미식"
    m_color = "orange" if is_restaurant else "purple"
    m_icon = "cutlery" if is_restaurant else "flag"

    folium.Marker(
        location=[target_place["lat"], target_place["lon"]],
        tooltip=f"목적지: {target_place['name']}",
        popup=f"<b>[목적지] {target_place['name']}</b><br>{target_place.get('desc', '')}",
        icon=folium.Icon(color=m_color, icon=m_icon, prefix="fa"),
    ).add_to(travel_map)

    # 실제 도로 경로 PolyLine
    if route_info and route_info["path"]:
        folium.PolyLine(
            locations=route_info["path"],
            color="#2563EB",
            weight=5,
            opacity=0.85,
            tooltip=f"{driving_dist}km / 약 {car_time}분 소요",
        ).add_to(travel_map)
    else:
        folium.PolyLine(
            locations=[[cur_lat, cur_lon], [target_place["lat"], target_place["lon"]]],
            color="gray",
            weight=3,
            dash_array="5, 8",
        ).add_to(travel_map)

    for p in filtered_places:
        if p["name"] != target_name:
            p_desc = p.get("desc") or p.get("admission_desc") or ""
            p_is_food = p.get("category") == "맛집/미식"
            p_color = "orange" if p_is_food else "blue"
            p_icon = "cutlery" if p_is_food else "info-sign"

            folium.Marker(
                location=[p["lat"], p["lon"]],
                tooltip=p["name"],
                popup=f"<b>{p['name']}</b><br>{p_desc}",
                icon=folium.Icon(color=p_color, icon=p_icon, prefix="fa" if p_is_food else None),
            ).add_to(travel_map)

    for att in waypoint_attractions:
        folium.Marker(
            location=[att["lat"], att["lon"]],
            tooltip=f"추천 경유지: {att['name']}",
            popup=f"<b>[추천 경유] {att['name']}</b><br>{att['address']}",
            icon=folium.Icon(color="cadetblue", icon="star"),
        ).add_to(travel_map)

    # 지도시각화
    st_folium(travel_map, width="100%", height=560, returned_objects=[])

    # 지도 하단 환율 계산기
    with st.expander("💱 해외 관광객용 원화(KRW) 환율 계산기 (8개국 통화 지원)", expanded=False):
        rates = get_exchange_rates("USD")
        if rates:
            krw_val = rates.get("KRW", 1340)

            currency_converters = {
                "USD": rates.get("USD", 1.0) / krw_val,
                "JPY": rates.get("JPY", 150.0) / krw_val,
                "EUR": rates.get("EUR", 0.9) / krw_val,
                "CNY": rates.get("CNY", 7.2) / krw_val,
                "TWD": rates.get("TWD", 32.0) / krw_val,
                "HKD": rates.get("HKD", 7.8) / krw_val,
                "GBP": rates.get("GBP", 0.78) / krw_val,
                "SGD": rates.get("SGD", 1.34) / krw_val,
            }

            default_calc = int(fuel_cost + toll_fare + admission_fee) if (fuel_cost + toll_fare + admission_fee) > 0 else 30000
            calc_krw = st.number_input("사용 금액 입력 (KRW 원)", min_value=0, value=default_calc, step=5000)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🇺🇸 미국 (USD)", f"${calc_krw * currency_converters['USD']:,.2f}")
            c2.metric("🇯🇵 일본 (JPY)", f"¥{calc_krw * currency_converters['JPY']:,.0f}")
            c3.metric("🇪🇺 유럽 (EUR)", f"€{calc_krw * currency_converters['EUR']:,.2f}")
            c4.metric("🇨🇳 중국 (CNY)", f"¥{calc_krw * currency_converters['CNY']:,.2f}")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("🇹🇼 대만 (TWD)", f"NT${calc_krw * currency_converters['TWD']:,.1f}")
            c6.metric("🇭🇰 홍콩 (HKD)", f"HK${calc_krw * currency_converters['HKD']:,.2f}")
            c7.metric("🇬🇧 영국 (GBP)", f"£{calc_krw * currency_converters['GBP']:,.2f}")
            c8.metric("🇸🇬 싱가포르 (SGD)", f"S${calc_krw * currency_converters['SGD']:,.2f}")
        else:
            st.info("환율 정보를 불러올 수 없습니다.")

    if waypoint_attractions:
        with st.expander("📍 경로 중간에 들르기 좋은 추천 스팟", expanded=False):
            w_cols = st.columns(len(waypoint_attractions))
            for idx, item in enumerate(waypoint_attractions):
                with w_cols[idx]:
                    st.markdown(f"**{item['name']}**")
                    st.caption(item["address"])
                    if item.get("url"):
                        st.markdown(f"[카카오맵 보기]({item['url']})")