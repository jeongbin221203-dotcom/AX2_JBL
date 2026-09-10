import os
import requests
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 0. 환경 변수 및 페이지 설정 (디버깅 프린트 제거)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")

load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("EXCHANGE_API_KEY")

st.set_page_config(
    page_title="글로벌 실시간 환율 서비스",
    page_icon="💱",
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
# 1. 헤더 UI
# ==========================================
st.markdown("<h1 class='main-title'>💱 글로벌 실시간 환율 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>ExchangeRate-API를 활용한 주요 통화 환율 정보 서비스</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ==========================================
# 2. API 호출 및 데이터 로직
# ==========================================
if not API_KEY:
    st.error("⚠️ API 키를 찾을 수 없습니다. 상위 폴더에 `.env` 파일과 `EXCHANGE_API_KEY` 설정이 올바른지 확인해주세요.")
else:
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

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