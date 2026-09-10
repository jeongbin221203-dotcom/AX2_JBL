import os
import requests
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 0. 환경 변수 및 페이지 설정 (절대 경로 추적)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")

load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("EXCHANGE_API_KEY")

st.set_page_config(
    page_title="실시간 환율 계산기",
    page_icon="🧮",
    layout="wide"
)

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
            font-size: 2.5rem;
        }
        
        .sub-title {
            color: #64748B;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }
        
        .calc-card {
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 전 세계 통화 국가명 매핑 딕셔너리 보강
# ==========================================
CURRENCY_COUNTRY_MAP = {
    "KRW": "대한민국", "USD": "미국", "JPY": "일본", "EUR": "유로존", "GBP": "영국",
    "CNY": "중국", "AUD": "호주", "CAD": "캐나다", "HKD": "홍콩", "NZD": "뉴질랜드",
    "SGD": "싱가포르", "CHF": "스위스", "THB": "태국", "VND": "베트남", "PHP": "필리핀",
    "IDR": "인도네시아", "MYR": "말레이시아", "INR": "인도", "TWD": "대만", "MXN": "멕시코",
    "BRL": "브라질", "ZAR": "남아프리카 공화국", "SEK": "스웨덴", "NOK": "노르웨이", "DKK": "덴마크",
    "PLN": "폴란드", "RUB": "러시아", "TRY": "튀르키예", "AED": "아랍에미리트", "SAR": "사우디아라비아",
    "ARS": "아르헨티나", "AMD": "아르메니아", "ANG": "네덜란드령 안틸레스", "AOA": "앙골라", "AWG": "아루바",
    "AZN": "아제르바이잔", "BAM": "보스니아 헤르체고비나", "BBD": "바베이도스", "BDT": "방글라데시", "BGN": "불가리아",
    "BHD": "바레인", "BIF": "부룬디", "BMD": "버뮤다", "BND": "브루나이", "BOB": "볼리비아",
    "BSD": "바하마", "BTN": "부탄", "BWP": "보츠와나", "BYN": "벨라루스", "BZD": "벨리즈",
    "CDF": "콩고 민주 공화국", "CLP": "칠레", "COP": "콜롬비아", "CRC": "코스타리카", "CUP": "쿠바",
    "CVE": "카보베르데", "CZK": "체코", "DJF": "지부티", "DOP": "도미니카 공화국", "DZD": "알제리",
    "EGP": "이집트", "ERN": "에리트레아", "ETB": "에티오피아", "FJD": "피지", "FKP": "포클랜드 제도",
    "FOK": "페로 제도", "GEL": "조지아", "GGP": "건지섬", "GHS": "가나", "GIP": "지브롤터",
    "GMD": "감비아", "GNF": "기니", "GTQ": "과테말라", "GYD": "가이아나", "HNL": "온두라스",
    "HRK": "크로아티아", "HTG": "아이티", "HUF": "헝가리", "ILS": "이스라엘", "IMP": "맨섬",
    "IQD": "이라크", "IRR": "이란", "ISK": "아이슬란드", "JEP": "저지섬", "JMD": "자메이카",
    "JOD": "요르단", "KES": "케냐", "KGS": "키르기스스탄", "KHR": "캄보디아", "KID": "키리바시",
    "KMF": "코모로", "KRW": "대한민국", "KWD": "쿠웨이트", "KYD": "케이맨 제도", "KZT": "카자흐스탄",
    "LAK": "라오스", "LBP": "레바논", "LKR": "스리랑카", "LRD": "라이베리아", "LSL": "레소토",
    "LYD": "리비아", "MAD": "모로코", "MDL": "몰도바", "MGA": "마다가스카르", "MKD": "북마케도니아",
    "MMK": "미얀마", "MNT": "몽골", "MOP": "마카오", "MRU": "모리타니", "MUR": "모리셔스",
    "MVR": "몰디브", "MWK": "말라위", "MXN": "멕시코", "MYR": "말레이시아", "MZN": "모잠비크",
    "NAD": "나미비아", "NGN": "나이지리아", "NIO": "니카라과", "NPR": "네팔", "NZD": "뉴질랜드",
    "OMR": "오만", "PAB": "파나마", "PEN": "페루", "PGK": "파푸아뉴기니", "PHP": "필리핀",
    "PKR": "파키스탄", "PLN": "폴란드", "PYG": "파라과이", "QAR": "카타르", "RON": "루마니아",
    "RSD": "세르비아", "RUB": "러시아", "RWF": "르완다", "SAR": "사우디아라비아", "SBD": "솔로몬 제도",
    "SCR": "세이셸", "SDG": "수단", "SEK": "스웨덴", "SGD": "싱가포르", "SHP": "세인트헬레나",
    "SLE": "시에라리온", "SLL": "시에라리온", "SOS": "소말리아", "SRD": "수리남", "SSP": "남수단",
    "STN": "상투메 프린시페", "SYP": "시리아", "SZL": "에스와티니", "THB": "태국", "TJS": "타지키스탄",
    "TMT": "투르크메니스탄", "TND": "튀니지", "TOP": "통가", "TRY": "튀르키예", "TTD": "트리니다드 토바고",
    "TVD": "투발루", "TWD": "대만", "TZS": "탄자니아", "UAH": "우크라이나", "UGX": "우간다",
    "USD": "미국", "UYU": "우루과이", "UZS": "우즈베키스탄", "VES": "베네수엘라", "VND": "베트남",
    "VUV": "바누아투", "WST": "사모아", "XAF": "중앙아프리카 CFA", "XCD": "동카리브", "XDR": "특별인출권",
    "XOF": "서아프리카 CFA", "XPF": "프랑스령 태평양 프랑", "YER": "예멘", "ZAR": "남아프리카 공화국",
    "ZMW": "잠비아", "ZWL": "짐바브웨"
}

# ==========================================
# 2. 헤더 UI
# ==========================================
st.markdown("<h1 class='main-title'>🧮 실시간 환율 계산기</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ExchangeRate-API를 활용하여 원하는 금액과 통화 간의 실시간 환산 결과를 계산합니다.</p>", unsafe_allow_html=True)

# ==========================================
# 3. API 데이터 로드 및 환산 로직
# ==========================================
if not API_KEY:
    st.error("⚠️ API 키를 찾을 수 없습니다. 상위 폴더에 `.env` 파일과 `EXCHANGE_API_KEY` 설정이 올바른지 확인해주세요.")
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
        
        # 드롭다운 표시 함수 (매핑에 없으면 통화 코드 자체를 국가명으로 대체하여 '기타 국가' 표시 원천 차단)
        def format_func(code):
            country = CURRENCY_COUNTRY_MAP.get(code, f"{code} 지역")
            return f"{code} ({country})"

        # 입력 레이아웃 구성
        col1, col2, col3 = st.columns([2, 0.8, 2])
        
        with col1:
            st.subheader("📤 보내는 통화")
            
            # 문자열 기반 입력으로 변경하여 쉼표 입력 지원 및 실시간 파싱
            raw_input_val = st.text_input("환전할 금액", value="15,000")
            
            try:
                # 쉼표 제거 후 실수형으로 변환
                amount = float(raw_input_val.replace(",", "").strip())
            except ValueError:
                amount = 0.0
                st.warning("⚠️ 올바른 숫자를 입력해주세요.")
            
            default_from_idx = raw_currencies.index("KRW") if "KRW" in raw_currencies else 0
            from_currency = st.selectbox("기준 통화 선택", raw_currencies, index=default_from_idx, format_func=format_func)
            
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 75px; font-size: 2rem;'>➡️</div>", unsafe_allow_html=True)
            
        with col3:
            st.subheader("📥 받는 통화")
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            
            default_to_idx = raw_currencies.index("USD") if "USD" in raw_currencies else 1
            to_currency = st.selectbox("환전할 통화 선택", raw_currencies, index=default_to_idx, format_func=format_func)

        # 환율 계산 (USD 기준 크로스 환율)
        amount_in_usd = amount / rates[from_currency] if rates[from_currency] > 0 else 0
        converted_amount = amount_in_usd * rates[to_currency]
        exchange_rate = rates[to_currency] / rates[from_currency] if rates[from_currency] > 0 else 0

        from_country = CURRENCY_COUNTRY_MAP.get(from_currency, from_currency)
        to_country = CURRENCY_COUNTRY_MAP.get(to_currency, to_currency)

        # 결과 출력 카드 (1,000 단위 쉼표 적용)
        st.markdown(f"""
            <div class="calc-card">
                <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 5px;">환산 결과</p>
                <h2 style="font-size: 2.2rem; font-weight: 700; margin: 10px 0px;">
                    {amount:,.2f} {from_currency} ({from_country}) = <span style="color: #FBBF24;">{converted_amount:,.2f} {to_currency} ({to_country})</span>
                </h2>
                <p style="font-size: 0.95rem; opacity: 0.8; margin-top: 10px;">
                    적용 환율: 1 {from_currency} = {exchange_rate:,.4f} {to_currency}
                </p>
            </div>
        """, unsafe_allow_html=True)