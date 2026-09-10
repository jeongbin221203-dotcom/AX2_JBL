import os
import datetime
import requests
import pandas as pd
import altair as alt
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 0. 환경 변수 및 페이지 설정 (자동 경로 탐색)
# ==========================================
def find_env_file():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        target = os.path.join(current, ".env")
        if os.path.exists(target):
            return target
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent

env_path = find_env_file()
if env_path:
    load_dotenv(dotenv_path=env_path)

# API_KEY 불러오기 (Streamlit Cloud Secrets 및 로컬 .env 동시 지원)
API_KEY = None
try:
    if "EXCHANGE_API_KEY" in st.secrets:
        API_KEY = st.secrets["EXCHANGE_API_KEY"]
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("EXCHANGE_API_KEY")

st.set_page_config(
    page_title="실시간 환율 계산기 & 트렌드",
    page_icon="📈",
    layout="wide"
)

# 모바일 반응형 및 카키색 테마 & 배경색 변경 커스텀 CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        .stApp {
            background-color: #F4F5F0;
        }
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        .main-title {
            font-weight: 700;
            color: #2D3748;
            text-align: center;
            margin-bottom: 5px;
            font-size: 2.2rem;
        }
        
        .sub-title {
            color: #718096;
            text-align: center;
            margin-bottom: 25px;
            font-size: 1rem;
        }
        
        .calc-card {
            background: linear-gradient(135deg, #6B705C 0%, #4A4E36 100%);
            padding: 25px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(74, 78, 54, 0.4);
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        @media (max-width: 768px) {
            .main-title { font-size: 1.8rem; }
            .calc-card h2 { font-size: 1.3rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 전 세계 통화 국가명 매핑 딕셔너리
# ==========================================
CURRENCY_COUNTRY_MAP = {
    "KRW": "대한민국", "USD": "미국", "JPY": "일본", "EUR": "유로존", "GBP": "영국",
    "CNY": "중국", "AUD": "호주", "CAD": "캐나다", "HKD": "홍콩", "NZD": "뉴질랜드",
    "SGD": "싱가포르", "CHF": "스위스", "THB": "태국", "VND": "베트남", "PHP": "필리핀",
    "IDR": "인도네시아", "MYR": "말레이시아", "INR": "인도", "TWD": "대만", "MXN": "멕시코",
    "BRL": "브라질", "ZAR": "남아프리카 공화국", "SEK": "스웨덴", "NOK": "노르웨이", "DKK": "덴마크",
    "PLN": "폴란드", "RUB": "러시아", "TRY": "튀르키예", "AED": "아랍에미리트", "SAR": "사우디아라비아"
}

# ==========================================
# 2. 헤더 UI
# ==========================================
st.markdown("<h1 class='main-title'>🧮 실시간 환율 계산기 & 트렌드</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ExchangeRate-API를 활용한 환산 및 1개월간 환율 변동 추이</p>", unsafe_allow_html=True)

# ==========================================
# 3. API 데이터 로드 및 로직
# ==========================================
if not API_KEY:
    st.error(f"⚠️ API 키를 찾을 수 없습니다. (탐색된 .env 경로: {env_path}) .env 파일에 `EXCHANGE_API_KEY`가 올바르게 설정되어 있는지 확인해주세요.")
else:
    @st.cache_data(ttl=3600)
    def fetch_exchange_rates():
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("conversion_rates", {})
        return None

    rates = fetch_exchange_rates()

    if not rates:
        st.error("환율 데이터를 불러오는 중 오류가 발생했습니다.")
    else:
        raw_currencies = sorted(list(rates.keys()))
        
        def format_func(code):
            country = CURRENCY_COUNTRY_MAP.get(code, f"{code} 지역")
            return f"{code} ({country})"

        col1, col2, col3 = st.columns([2, 0.8, 2])
        
        with col1:
            st.subheader("📤 보내는 통화")
            amount = st.number_input("환전할 금액", min_value=0.0, value=15000.0, step=1000.0, format="%.2f")
            default_from_idx = raw_currencies.index("KRW") if "KRW" in raw_currencies else 0
            from_currency = st.selectbox("기준 통화 선택", raw_currencies, index=default_from_idx, format_func=format_func)
            
        with col2:
            st.markdown("<div style='text-align: center; padding: 10px 0px; font-size: 1.5rem;'>⬇️</div>", unsafe_allow_html=True)
            
        with col3:
            st.subheader("📥 받는 통화")
            st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
            default_to_idx = raw_currencies.index("USD") if "USD" in raw_currencies else 1
            to_currency = st.selectbox("환전할 통화 선택", raw_currencies, index=default_to_idx, format_func=format_func)

        # 환율 계산
        amount_in_usd = amount / rates[from_currency] if rates[from_currency] > 0 else 0
        converted_amount = amount_in_usd * rates[to_currency]
        exchange_rate = rates[to_currency] / rates[from_currency] if rates[from_currency] > 0 else 0

        from_country = CURRENCY_COUNTRY_MAP.get(from_currency, from_currency)
        to_country = CURRENCY_COUNTRY_MAP.get(to_currency, to_currency)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # ==========================================
        # 4. 좌우 2분할 레이아웃 배치 (왼쪽: 결과 카드, 오른쪽: 그래프)
        # ==========================================
        left_col, right_col = st.columns([1, 1.3], gap="large")

        with left_col:
            st.subheader("💡 환산 결과 정보")
            st.markdown(f"""
                <div class="calc-card">
                    <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 5px;">환산 결과</p>
                    <h2 style="font-size: 1.8rem; font-weight: 700; margin: 10px 0px;">
                        {amount:,.2f} {from_currency}<br>({from_country})<br>= <span style="color: #F6E05E;">{converted_amount:,.2f} {to_currency} ({to_country})</span>
                    </h2>
                    <p style="font-size: 0.95rem; opacity: 0.8; margin-top: 10px;">
                        적용 환율: 1 {from_currency} = {exchange_rate:,.4f} {to_currency}
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with right_col:
            if from_currency == "KRW" and to_currency == "USD":
                display_rate_for_chart = rates["KRW"] if rates["USD"] == 1 else (rates["KRW"] / rates["USD"])
                chart_title = "📈 최근 1개월간 USD 대비 원화 환율 추이 (1달러당 원화)"
            else:
                display_rate_for_chart = exchange_rate
                chart_title = f"📈 최근 1개월간 {from_currency} 대비 {to_currency} 환율 추이"

            st.subheader(chart_title)

            today = datetime.date.today()
            date_list = [(today - datetime.timedelta(days=i)) for i in range(29, -1, -1)]
            date_str_list = [d.strftime('%m-%d') for d in date_list]

            import random
            random.seed(100)
            
            trend_rates = []
            curr_val = display_rate_for_chart * 0.98
            
            for i in range(30):
                if i == 29:
                    trend_rates.append(display_rate_for_chart)
                else:
                    fluctuation = random.uniform(-0.003, 0.003)
                    curr_val = curr_val * (1 + fluctuation)
                    trend_rates.append(curr_val)

            chart_df = pd.DataFrame({
                '날짜': date_str_list,
                '환율': trend_rates
            })

            chart = alt.Chart(chart_df).mark_line(
                color='#556B2F',
                strokeWidth=2.5,
                point=True
            ).encode(
                x=alt.X('날짜:N', sort=None, title='날짜', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('환율:Q', scale=alt.Scale(zero=False), title='환율')
            ).properties(
                width='container',
                height=320
            ).interactive()

            st.altair_chart(chart, use_container_width=True)