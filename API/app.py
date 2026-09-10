# 날씨 API 실습
# https://home.openweathermap.org/api_keys 현재 날씨 API 특정 지역의 날씨를 가져와 출력
# 사전준비 API 발급
# env에  key 넣으면 안됨
# pip install requests python-dotenv 활용
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은 API KEY
# .env.example OPENWEATHER_API_KET=your_key
# .env.example 받아서 .env로 이름 바꾸고 자기 API를 채운다.


import os
import datetime
import requests
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 0. 페이지 설정 및 경로 설정 (로컬 & 클라우드 공용)
# ==========================================
st.set_page_config(
    page_title="글로벌 종합 정보 대시보드",
    page_icon="🌍",
    layout="wide"
)

# 상위 폴더 경로 계산 (.env 탐색용)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)

# API 키 안전하게 불러오기 (클라우드 Secrets 또는 로컬 .env 자동 대응)
WEATHER_API_KEY = None
EXCHANGE_API_KEY = None

try:
    WEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KET")
    EXCHANGE_API_KEY = st.secrets.get("EXCHANGE_API_KEY")
except:
    pass

if not WEATHER_API_KEY:
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KET")

if not EXCHANGE_API_KEY:
    EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")


# 모바일 및 PC 반응형 커스텀 CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        .main-title {
            font-weight: 700;
            color: #1E293B;
            text-align: center;
            margin-bottom: 5px;
            font-size: 2.3rem;
        }
        
        .sub-title {
            color: #64748B;
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.1rem;
        }
        
        .weather-main-card {
            background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.4);
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        
        .exchange-main-card {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.4);
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        
        .info-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            height: 100%;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        .info-label {
            color: #64748B;
            font-size: 1rem;
            margin-bottom: 5px;
            font-weight: 500;
        }
        
        .info-value {
            color: #0F172A;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 사이드바 메뉴 네비게이션
# ==========================================
st.sidebar.title("📌 메뉴 선택")
app_mode = st.sidebar.radio("원하시는 서비스를 선택하세요:", ["🌤️ 실시간 날씨 정보", "💱 실시간 환율 정보"])

# ==========================================
# [탭 1] 실시간 날씨 정보 앱
# ==========================================
if app_mode == "🌤️ 실시간 날씨 정보":
    st.markdown("<h1 class='main-title'>🌤️ 글로벌 실시간 날씨 대시보드</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>OpenWeatherMap API를 활용한 기상 정보 서비스</p>", unsafe_allow_html=True)

    # 한글 검색 매핑 딕셔너리
    KOR_TO_ENG_CITY = {
        "서울": "Seoul", "서울시": "Seoul", "서울특별시": "Seoul",
        "부산": "Busan", "부산시": "Busan", "부산광역시": "Busan",
        "인천": "Incheon", "인천시": "Incheon", "인천광역시": "Incheon",
        "대구": "Daegu", "대구시": "Daegu", "대구광역시": "Daegu",
        "대전": "Daejeon", "대전시": "Daejeon", "대전광역시": "Daejeon",
        "광주": "Gwangju", "광주시": "Gwangju", "광주광역시": "Gwangju",
        "울산": "Ulsan", "울산시": "Ulsan", "울산광역시": "Ulsan",
        "세종": "Sejong", "세종시": "Sejong", "세종특별자치시": "Sejong",
        "제주": "Jeju", "제주시": "Jeju", "제주도": "Jeju", "서귀포": "Seogwipo",
        "수원": "Suwon", "수원시": "Suwon",
        "성남": "Seongnam", "성남시": "Seongnam", "분당": "Bundang",
        "고양": "Goyang", "고양시": "Goyang", "일산": "Ilsan",
        "용인": "Yongin", "용인시": "Yongin",
        "창원": "Changwon", "창원시": "Changwon",
        "천안": "Cheonan", "천안시": "Cheonan",
        "청주": "Cheongju", "청주시": "Cheongju",
        "전주": "Jeonju", "전주시": "Jeonju",
        "춘천": "Chuncheon", "춘천시": "Chuncheon",
        "강릉": "Gangneung", "강릉시": "Gangneung",
        "포항": "Pohang", "포항시": "Pohang",
        "안양": "Anyang", "안양시": "Anyang",
        "부천": "Bucheon", "부천시": "Bucheon",
        "남양주": "Namyangju", "남양주시": "Namyangju",
        "화성": "Hwaseong", "화성시": "Hwaseong",
        "평택": "Pyeongtaek", "평택시": "Pyeongtaek"
    }

    col_space1, col_search, col_space2 = st.columns([1, 2, 1])
    with col_search:
        search_query = st.text_input("🌍 도시 이름을 검색하세요 (예: 서울, 제주, London, Tokyo)", value="서울", placeholder="도시 이름 입력...")

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    if not WEATHER_API_KEY:
        st.error("오류: OpenWeatherMap API 키를 찾을 수 없습니다. `.env` 파일 또는 Secrets 설정을 확인하세요.")
    else:
        if search_query:
            clean_query = search_query.strip()
            api_city_query = KOR_TO_ENG_CITY.get(clean_query, clean_query)

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={api_city_query}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={api_city_query}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
            
            try:
                w_res = requests.get(weather_url, timeout=10)
                w_data = w_res.json()
                
                if w_res.status_code == 200:
                    city_name = w_data["name"]
                    country = w_data["sys"]["country"]
                    temp = round(w_data["main"]["temp"], 1)
                    feels_like = round(w_data["main"]["feels_like"], 1)
                    humidity = w_data["main"]["humidity"]
                    wind_speed = w_data["wind"]["speed"]
                    pressure = w_data["main"]["pressure"]
                    clouds = w_data["clouds"]["all"]
                    desc = w_data["weather"][0]["description"]
                    icon_code = w_data["weather"][0]["icon"]
                    
                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
                    
                    today_min = temp
                    today_max = temp
                    
                    f_res = requests.get(forecast_url, timeout=10)
                    if f_res.status_code == 200:
                        f_data = f_res.json()
                        tz_offset = f_data["city"]["timezone"]
                        
                        first_dt_local = f_data["list"][0]["dt"] + tz_offset
                        today_date_str = datetime.datetime.utcfromtimestamp(first_dt_local).strftime('%Y-%m-%d')
                        
                        daily_temps = []
                        for item in f_data["list"]:
                            local_dt = item["dt"] + tz_offset
                            local_date = datetime.datetime.utcfromtimestamp(local_dt).strftime('%Y-%m-%d')
                            if local_date == today_date_str:
                                daily_temps.append(item["main"]["temp_min"])
                                daily_temps.append(item["main"]["temp_max"])
                                
                        if daily_temps:
                            today_min = round(min(daily_temps), 1)
                            today_max = round(max(daily_temps), 1)

                    col_left, col_right = st.columns([1.2, 1], gap="large")
                    
                    with col_left:
                        display_city_name = clean_query if clean_query in KOR_TO_ENG_CITY else city_name
                        st.markdown(f"""
                            <div class="weather-main-card">
                                <h2 style="margin-bottom: 0px; opacity: 0.9;">📍 {display_city_name}, {country}</h2>
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <div>
                                        <h1 style="font-size: 4.5rem; font-weight: 700; margin: 10px 0px;">{temp}°C</h1>
                                        <p style="font-size: 1.3rem; margin-bottom: 5px;"><strong>{desc}</strong> (체감 {feels_like}°C)</p>
                                        <p style="opacity: 0.9; margin: 0px; background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 8px; display: inline-block;">
                                            오늘 최저 <b>{today_min}°C</b> / 최고 <b>{today_max}°C</b>
                                        </p>
                                    </div>
                                    <img src="{icon_url}" style="width: 150px; filter: drop-shadow(0px 5px 10px rgba(0,0,0,0.2));" />
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_right:
                        r1_c1, r1_c2 = st.columns(2)
                        r2_c1, r2_c2 = st.columns(2)
                        
                        with r1_c1:
                            st.markdown(f"""
                                <div class="info-card">
                                    <p class="info-label">💧 습도</p>
                                    <p class="info-value">{humidity} <span style="font-size: 1rem;">%</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                        with r1_c2:
                            st.markdown(f"""
                                <div class="info-card">
                                    <p class="info-label">💨 풍속</p>
                                    <p class="info-value">{wind_speed} <span style="font-size: 1rem;">m/s</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                        with r2_c1:
                            st.markdown(f"""
                                <div class="info-card">
                                    <p class="info-label">🔽 기압</p>
                                    <p class="info-value">{pressure} <span style="font-size: 1rem;">hPa</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                        with r2_c2:
                            st.markdown(f"""
                                <div class="info-card">
                                    <p class="info-label">☁️ 구름양 (운량)</p>
                                    <p class="info-value">{clouds} <span style="font-size: 1rem;">%</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning(f"❌ '{clean_query}' 도시를 찾을 수 없습니다. (에러 코드: {w_res.status_code})")
            except requests.exceptions.RequestException as e:
                st.error(f"연결 실패: {e}")

# ==========================================
# [탭 2] 실시간 환율 정보 앱
# ==========================================
elif app_mode == "💱 실시간 환율 정보":
    st.markdown("<h1 class='main-title'>💱 글로벌 실시간 환율 대시보드</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>ExchangeRate-API를 활용한 주요 통화 환율 정보 서비스</p>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    if not EXCHANGE_API_KEY:
        st.error("오류: 환율 API 키를 찾을 수 없습니다. 상위 폴더의 `.env` 파일에 `EXCHANGE_API_KEY` 설정이 올바른지 확인해주세요.")
    else:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"

        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get("conversion_rates", {})
                
                krw_rate = rates.get("KRW") 
                jpy_rate = rates.get("JPY") 
                eur_rate = rates.get("EUR") 
                gbp_rate = rates.get("GBP")
                
                jpy_to_krw = (krw_rate / jpy_rate) * 100 if (krw_rate and jpy_rate) else 0
                eur_to_krw = krw_rate / eur_rate if (krw_rate and eur_rate) else 0
                gbp_to_krw = krw_rate / gbp_rate if (krw_rate and gbp_rate) else 0

                col_left, col_right = st.columns([1.2, 1], gap="large")
                
                with col_left:
                    st.markdown(f"""
                        <div class="exchange-main-card">
                            <h2 style="margin-bottom: 0px; opacity: 0.9;">🇺🇸 미국 기준통화 (USD)</h2>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <h1 style="font-size: 3.8rem; font-weight: 700; margin: 10px 0px;">{krw_rate:,.2f}원</h1>
                                    <p style="font-size: 1.2rem; margin-bottom: 5px;"><strong>1 미국 달러(USD)</strong> 당 원화 환율</p>
                                    <p style="opacity: 0.9; margin: 0px; background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 8px; display: inline-block;">
                                        기준 통화: <b>USD ($)</b> 실시간 연동중
                                    </p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_right:
                    r1_c1, r1_c2 = st.columns(2)
                    r2_c1, r2_c2 = st.columns(2)
                    
                    with r1_c1:
                        st.markdown(f"""
                            <div class="info-card">
                                <p class="info-label">🇯🇵 일본 엔 (JPY)</p>
                                <p class="info-value">{jpy_to_krw:,.2f} <span style="font-size: 0.9rem;">원/100엔</span></p>
                            </div>
                        """, unsafe_allow_html=True)
                    with r1_c2:
                        st.markdown(f"""
                            <div class="info-card">
                                <p class="info-label">🇪🇺 유럽 유로 (EUR)</p>
                                <p class="info-value">{eur_to_krw:,.2f} <span style="font-size: 0.9rem;">원/유로</span></p>
                            </div>
                        """, unsafe_allow_html=True)
                    with r2_c1:
                        st.markdown(f"""
                            <div class="info-card">
                                <p class="info-label">🇬🇧 영국 파운드 (GBP)</p>
                                <p class="info-value">{gbp_to_krw:,.2f} <span style="font-size: 0.9rem;">원/파운드</span></p>
                            </div>
                        """, unsafe_allow_html=True)
                    with r2_c2:
                        st.markdown(f"""
                            <div class="info-card">
                                <p class="info-label">📊 데이터 상태</p>
                                <p class="info-value" style="color: #10B981; font-size: 1.3rem;">정상 연동</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error(f"API 호출 에러: 상태 코드 {response.status_code}")
        except Exception as e:
            st.error(f"연결 실패: {e}")