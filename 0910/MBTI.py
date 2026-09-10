import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 0. 페이지 설정 및 Streamlit 기본 이미지 툴바(도형) 완전 제거 CSS
# ==========================================
st.set_page_config(
    page_title="무역 직무 MBTI 진단 센터", 
    page_icon="🌐", 
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        .main-title {
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0px;
        }
        
        .option-card {
            background-color: #F8FAFC;
            border: 2px solid #E2E8F0;
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
        }
        
        .option-card:hover {
            border-color: #3B82F6;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.1);
        }

        /* 💡 [핵심] 사진 위에 뜨는 Streamlit 기본 툴바(회색 둥근 상자/도형) 강제 숨김 처리 */
        [data-testid="stImageToolbar"] {
            display: none !important;
        }
        
        .stImage {
            margin-bottom: 0px !important;
        }
        
        .stImage img {
            height: 180px !important;
            width: 100% !important;
            object-fit: cover !important;
            border-radius: 12px !important;
        }

        .result-box {
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            padding: 30px;
            border-radius: 16px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
        }
        
        .fit-box {
            background-color: #F8FAFC;
            border-left: 5px solid #3B82F6;
            padding: 20px;
            border-radius: 0 12px 12px 0;
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
            margin-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 16가지 MBTI 전체 무역 직무 정의
# ==========================================
JOB_DESCRIPTIONS = {
    "ESTJ": {
        "job": "해상/항공 물류 및 SCM 관리자",
        "desc": "철저한 일정 관리와 원칙 중심의 프로세스 조율로 복잡한 글로벌 공급망(SCM)을 안정적으로 통제하는 데 탁월합니다.",
        "skills": ["스케줄링", "공급망 관리", "위기 대응"],
        "connection": "체계적이고 원칙을 중시하는 **ESTJ**의 성향은 수백 개의 화물 스케줄과 엄격한 납기를 통제해야 하는 SCM/물류 관리 업무의 핵심 역량인 '프로세스 통제력'과 직결됩니다.",
        "image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80"
    },
    "ENTJ": {
        "job": "해외영업 및 글로벌 전략기획자",
        "desc": "목표 지향적인 추진력과 전략적 사고로 신규 해외 시장을 개척하고 바이어와의 협상을 주도하는 리더형 인재입니다.",
        "skills": ["바이어 협상", "해외시장 개척", "전략 기획"],
        "connection": "목표 달성에 대한 강한 집념과 리더십을 지닌 **ENTJ**는 불확실한 해외 거시 시장을 뚫고 바이어와의 협상 주도권을 쥐어야 하는 해외영업 및 전략 기획 직무와 완벽한 시너지를 냅니다.",
        "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=800&q=80"
    },
    "ISTJ": {
        "job": "수출입 서류 및 통관/관세 관리자",
        "desc": "세심하고 정확한 데이터 처리 능력으로 선적서류(B/L, 인보이스) 및 관세/통관 절차를 완벽하게 수행합니다.",
        "skills": ["서류 검증", "관세법 이해", "데이터 정확성"],
        "connection": "사소한 오탈자 하나도 용납하지 않는 꼼꼼함과 책임감을 가진 **ISTJ**는 수십 가지의 까다로운 무역 서류(B/L, L/C, 인보이스)를 무결점으로 검증해야 하는 통관·서류 관리 업무에 최적화되어 있습니다.",
        "image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80"
    },
    "INTJ": {
        "job": "글로벌 무역 데이터 분석가",
        "desc": "방대한 무역 통계와 시장 데이터를 심층적으로 분석하여 객관적인 인사이트를 도출하고 최적의 무역 전략을 제시합니다.",
        "skills": ["데이터 분석", "시장 조사", "리스크 예측"],
        "connection": "구조적이고 독립적으로 사고하는 **INTJ**의 성향은 방대한 글로벌 무역 통계 데이터 속에서 숨겨진 패턴과 리스크를 읽어내어 객관적인 인사이트를 도출하는 데이터 분석 업무에 강력한 무기가 됩니다.",
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
    },
    "ESFJ": {
        "job": "해외 고객 만족(CS) 및 영업지원 전문가",
        "desc": "원활한 소통 능력과 친화력으로 해외 파트너 및 고객사와의 관계를 유지하고 사내 유관 부서 간의 원활한 조율을 돕습니다.",
        "skills": ["고객 커뮤니케이션", "부서 간 조율", "영업 지원"],
        "connection": "타인의 감정을 잘 헤아리고 협력을 이끌어내는 **ESFJ**의 친화력은 해외 파트너사와의 우호적인 관계를 유지하고 영업 부서와 물류 부서 간의 갈등을 원만히 조율하는 데 핵심적인 역할을 합니다.",
        "image": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=800&q=80"
    },
    "ENFJ": {
        "job": "해외 지사 관리 및 글로벌 인사(HR) 담당자",
        "desc": "탁월한 리더십과 공감 능력을 바탕으로 해외 현지 법인의 조직 문화를 다지고 파트너사들과 우호적인 협력 관계를 구축합니다.",
        "skills": ["조직 관리", "글로벌 소통", "관계 구축"],
        "connection": "사람 중심의 따뜻한 리더십을 갖춘 **ENFJ**는 문화와 언어가 다른 해외 현지 법인 임직원들을 하나로 아우르고, 글로벌 파트너사와의 신뢰 기반 네트워크를 구축하는 데 탁월한 역량을 발휘합니다.",
        "image": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80"
    },
    "ISFJ": {
        "job": "무역 금융 및 네고(Nego) 담당자",
        "desc": "신용장(L/C) 조건 검토와 은행 네고 업무에서 놀라운 꼼꼼함과 책임감을 발휘하여 자금 흐름의 안전성을 확보합니다.",
        "skills": ["신용장(L/C)", "무역 금융", "철저한 검증"],
        "connection": "안정성을 지향하고 맡은 일을 묵묵히 완수하는 **ISFJ**는 기업의 생명줄과도 같은 대금 회수와 무역 금융(L/C 네고)의 엄격한 은행 서류 조건을 오차 없이 이행하는 데 완벽하게 부합합니다.",
        "image": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=800&q=80"
    },
    "INFJ": {
        "job": "글로벌 컴플라이언스 및 무역 윤리 기획자",
        "desc": "국제 무역 규제와 윤리 경영 지침을 면밀히 살피며 기업이 글로벌 법적 리스크 없이 건전하게 성장하도록 돕습니다.",
        "skills": ["규제 준수", "윤리 경영", "리스크 방지"],
        "connection": "깊은 통찰력과 직관, 그리고 도덕적 신념이 강한 **INFJ**는 복잡하게 급변하는 국제 무역 제재와 컴플라이언스 규정을 해석하고, 기업이 윤리적이고 안전한 글로벌 경영을 하도록 가이드하는 역할을 잘 소화합니다.",
        "image": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=800&q=80"
    },
    "ESTP": {
        "job": "해외 현장 영업 및 위기대응 트레이더",
        "desc": "빠른 상황 판단력과 대담한 실행력으로 긴박한 해외 현장 미팅이나 돌발 무역 이슈를 즉각적으로 해결합니다.",
        "skills": ["현장 대처", "빠른 결단", "협상 돌파력"],
        "connection": "임기응변에 강하고 행동력이 뛰어난 **ESTP**는 예측 불가능한 변수가 가득한 글로벌 현장 무역 무대에서 실시간 돌발 상황을 유연하게 돌파하고 계약을 성사시키는 데 최적화되어 있습니다.",
        "image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80"
    },
    "ENTP": {
        "job": "글로벌 신사업 발굴 및 해외벤처 기획자",
        "desc": "틀에 박히지 않은 창의적인 아이디어로 기존에 없던 해외 신시장 비즈니스 모델을 기획하고 판을 주도합니다.",
        "skills": ["아이디어 기획", "시장 혁신", "도전 정신"],
        "connection": "새로운 가능성을 탐구하는 것을 즐기는 **ENTP**는 기존 무역 관행에 얽매이지 않고, 해외 유망 신사업 아이템을 발굴하며 글로벌 시장의 판을 새롭게 짜는 기획 업무와 궁합이 좋습니다.",
        "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80"
    },
    "ISTP": {
        "job": "무역 물류 시스템 및 인프라 운영자",
        "desc": "복잡한 물류 창고 시스템과 스마트 항만 인프라의 기술적 문제를 냉철하게 분석하고 최적화합니다.",
        "skills": ["기술적 분석", "시스템 운영", "효율화"],
        "connection": "분석적이고 실용적인 문제 해결 능력을 지닌 **ISTP**는 물류 자동화 센터나 스마트 항만 등 무역 인프라 시스템의 작동 원리를 파악하고 효율성을 극대화하는 실무에 강합니다.",
        "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
    },
    "INTP": {
        "job": "글로벌 경제 및 환율 리스크 연구원",
        "desc": "깊이 있는 통찰력으로 환율 변동과 국제 거시경제 지표를 분석하여 기업의 환위험 헤지 전략을 수립합니다.",
        "skills": ["거시경제 분석", "환율 헤지", "이론적 통찰"],
        "connection": "지적 호기심이 많고 논리적 체계를 파고드는 **INTP**는 환율, 금리, 지정학적 리스크 등 글로벌 거시경제 변수를 심도 있게 파고들어 기업의 재무적 방어 전략을 수립하는 데 탁월합니다.",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80"
    },
    "ESFP": {
        "job": "해외 전시회 및 글로벌 마케터",
        "desc": "활기찬 에너지와 타고난 사교성으로 해외 대형 박람회나 전시회에서 바이어들의 이목을 사로잡습니다.",
        "skills": ["이벤트 기획", "대외 홍보", "활기찬 소통"],
        "connection": "사람들 속에서 에너지를 얻고 분위기를 주도하는 **ESFP**의 사교성은 글로벌 무역 박람회 현장에서 바이어를 맞이하고 자사 제품을 대외적으로 홍보하는 마케팅 활동에 최적입니다.",
        "image": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80"
    },
    "ENFP": {
        "job": "해외 인플루언서 마케팅 및 글로벌 PR 전문가",
        "desc": "트렌드를 읽어내는 감각과 열정적인 에너지로 글로벌 SNS 채널과 해외 파트너십 마케팅을 성공적으로 이끕니다.",
        "skills": ["트렌드 창출", "콘텐츠 기획", "글로벌 PR"],
        "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
        "connection": "열정이 넘치고 트렌드에 민감한 **ENFP**는 전 세계 소비자의 마음을 사로잡을 글로벌 디지털 마케팅 캠페인을 기획하고 대외 소통을 이끌어내는 데 최고의 역량을 발휘합니다."
    },
    "ISFP": {
        "job": "글로벌 소싱 및 디자인 디렉터",
        "desc": "섬세한 감각과 미적 기준을 바탕으로 해외에서 우수한 디자인 상품과 유니크한 소비재를 발굴합니다.",
        "skills": ["디자인 감각", "유니크 소싱", "섬세한 취향"],
        "image": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
        "connection": "예술적이고 섬세한 감각을 지닌 **ISFP**는 시장의 트렌드 변화와 심미적 가치를 빠르게 캐치하여, 해외 시장에서 감각적인 소비재나 라이프스타일 아이템을 발굴하는 소싱 업무에 적합합니다."
    },
    "INFP": {
        "job": "글로벌 소싱 및 친환경 무역 기획자",
        "desc": "창의적인 시각과 윤리적 가치를 바탕으로 지속 가능한 친환경 공급망을 발굴하고 새로운 글로벌 소싱 아이템을 기획합니다.",
        "skills": ["친환경 소싱", "창의적 기획", "글로벌 트렌드 파악"],
        "image": "https://images.unsplash.com/photo-1497436072909-60f360e1d4b1?auto=format&fit=crop&w=800&q=80",
        "connection": "자신의 가치관과 의미를 중요하게 여기는 **INFP**는 최근 글로벌 무역의 화두인 ESG 경영 및 지속 가능한 친환경 공급망 구축 기획 업무와 정신적인 결이 맞닿아 있습니다."
    }
}

# ==========================================
# 2. 20문항 정의
# ==========================================
QUESTIONS = [
    {
        "q": "대규모 해외 출장이나 네트워킹 행사를 마치고 숙소로 돌아왔을 때 나의 상태는?", 
        "options": ["새로운 사람들을 많이 만나 에너지가 오히려 충전되고 활기차다.", "많은 사람들과 교류하느라 기력이 소진되어 혼자만의 휴식이 절실하다."], 
        "axis": "EI", "val_a": "E", "val_b": "I",
        "img_a": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "글로벌 프로젝트 회의 중 아이디어를 개진할 때 나는?", 
        "options": ["말을 하면서 생각을 정리하는 편이라 회의 중에 적극적으로 발언한다.", "머릿속으로 완벽하게 논리를 정리한 뒤 조용히 핵심만 말하는 것을 선호한다."], 
        "axis": "EI", "val_a": "E", "val_b": "I",
        "img_a": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "평소 업무를 처리하거나 사내 커뮤니케이션을 할 때 선호하는 방식은?", 
        "options": ["직접 찾아가서 구두로 대화하거나 화상 미팅을 통해 빠르게 소통한다.", "오해의 소지를 없애고 기록이 남는 메신저나 이메일 소통을 선호한다."], 
        "axis": "EI", "val_a": "E", "val_b": "I",
        "img_a": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "새로운 해외 바이어나 파트너사를 처음 만나는 자리가 잡혔을 때?", 
        "options": ["새로운 인맥을 넓힌다는 생각에 기대감이 크고 쉽게 친해진다.", "처음 보는 사람들과의 어색함을 풀고 대화를 이어가는 과정이 다소 피로하다."], 
        "axis": "EI", "val_a": "E", "val_b": "I",
        "img_a": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "팀 내에서 내가 주로 맡는 역할이나 선호하는 포지션은?", 
        "options": ["모임을 주도하거나 대외 협상 및 발표 전면에 나서는 편이다.", "조용히 뒤에서 서포트하거나 깊이 있게 실무를 분석하고 파고드는 편이다."], 
        "axis": "EI", "val_a": "E", "val_b": "I",
        "img_a": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "새로운 무역 실무 매뉴얼이나 관세법 개정안을 읽을 때 나는?", 
        "options": ["지금 당장 내 업무와 실무에 적용되는 구체적인 조항과 팩트에 집중한다.", "이 법 개정이 앞으로 글로벌 무역 시장 전체 흐름에 미칠 함의와 트렌드를 본다."], 
        "axis": "SN", "val_a": "S", "val_b": "N",
        "img_a": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "과거 수출입 실적 데이터를 검토할 때 나의 초점은?", 
        "options": ["실제 발생한 거래 건수, 선적일, 금액 등 눈에 보이는 정확한 수치다.", "데이터 속에 나타난 장기적인 증감 추세와 이면의 시장 가능성이다."], 
        "axis": "SN", "val_a": "S", "val_b": "N",
        "img_a": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "새로운 해외 소싱 아이템을 발굴할 때 나는?", 
        "options": ["이미 시장에서 검증되어 안정적으로 수요가 있는 베스트셀러 품목을 선호한다.", "아직 대중화되지 않았지만 미래 가치가 높아 보이는 독창적인 아이템에 끌린다."], 
        "axis": "SN", "val_a": "S", "val_b": "N",
        "img_a": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1497436072909-60f360e1d4b1?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "업무 문제를 해결할 때 평소 나의 접근 방식은?", 
        "options": ["과거에 성공했거나 표준화되어 검증된 프로세스를 그대로 따른다.", "틀에 박히지 않은 새로운 방식을 상상해보고 창의적인 해결책을 시도한다."], 
        "axis": "SN", "val_a": "S", "val_b": "N",
        "img_a": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "미래의 무역 물류 환경이나 글로벌 경제를 상상할 때 나는?", 
        "options": ["당장 내년에 도입될 물류 자동화 기술이나 현실적인 인프라 개선을 생각한다.", "수십 년 뒤 완전 무인화된 글로벌 공급망이나 완전히 바뀔 경제 구조를 그린다."], 
        "axis": "SN", "val_a": "S", "val_b": "N",
        "img_a": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "무역 계약 조건이나 단가 협상에서 가장 중요하게 여기는 기준은?", 
        "options": ["철저하게 득실을 따져 우리 회사에 유리한 논리적 근거와 이익이다.", "상대방과의 신뢰 관계 및 향후 장기적인 파트너십 유지 여부다."], 
        "axis": "TF", "val_a": "T", "val_b": "F",
        "img_a": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1577495508048-b635879837f1?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "동료나 팀원이 업무상 큰 실수를 저질러 회사에 손실이 생겼을 때?", 
        "options": ["어디서부터 잘못되었는지 냉정하게 원인을 분석하고 책임을 규명한다.", "당사자가 받을 충격과 속상한 마음을 먼저 공감하고 위로해 준다."], 
        "axis": "TF", "val_a": "T", "val_b": "F",
        "img_a": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "바이어의 무리한 클레임 요구를 거절해야 하는 상황에서 나는?", 
        "options": ["계약서 조항과 인코텀즈 원칙을 들이밀며 객관적 팩트로 단호하게 거절한다.", "상대방의 입장을 충분히 이해한다는 점을 어필하며 부드럽게 양해를 구한다."], 
        "axis": "TF", "val_a": "T", "val_b": "F",
        "img_a": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "사내 성과 평가나 업무 분장을 정할 때 공정함의 기준은?", 
        "options": ["누가 더 객관적인 성과를 내고 기여했는가 하는 명확한 지표와 실적이다.", "각자의 개인 사정과 업무 스트레스, 팀 내 기여 분위기 등 상황적 맥락이다."], 
        "axis": "TF", "val_a": "T", "val_b": "F",
        "img_a": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "다른 사람의 의견에 피드백을 줄 때 나의 화법은?", 
        "options": ["효율성과 논리적 타당성을 중심으로 개선해야 할 점을 직설적으로 짚어준다.", "상처받지 않도록 칭찬과 격려를 섞어가며 부드럽게 제안한다."], 
        "axis": "TF", "val_a": "T", "val_b": "F",
        "img_a": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "일주일치 업무 스케줄이나 출장 계획을 세울 때 나는?", 
        "options": ["시간대별로 해야 할 일을 완벽하게 리스트업하고 철저히 통제하며 지킨다.", "큰 일정만 잡아두고 그날그날 상황에 맞춰 유연하게 대처하는 편이다."], 
        "axis": "JP", "val_a": "J", "val_b": "P",
        "img_a": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "마감 기한이 정해진 장기 프로젝트를 진행할 때 나의 태도는?", 
        "options": ["미리미터 단위로 마감일을 쪼개어 여유 있게 미리 결과물을 완성해 둔다.", "마감 직전에 집중력을 폭발적으로 끌어올려 단숨에 몰아쳐서 끝낸다."], 
        "axis": "JP", "val_a": "J", "val_b": "P",
        "img_a": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "업무 중 갑작스럽게 스케줄이 변경되거나 돌발 변수가 발생했을 때?", 
        "options": ["원래 세워둔 계획이 틀어져 스트레스를 받지만 신속하게 플랜 B를 가동한다.", "예상치 못한 변수를 흥미롭게 여기며 즉흥적으로 대안을 찾아 즐긴다."], 
        "axis": "JP", "val_a": "J", "val_b": "P",
        "img_a": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "내 책상 위나 업무용 PC 바탕화면의 파일 정돈 상태는?", 
        "options": ["폴더별, 날짜별로 칼같이 분류되어 있어 누구나 찾아보기 쉽게 정리되어 있다.", "내 머릿속에 다 들어있으므로 임시 파일이 자유롭게 흩어져 있는 편이다."], 
        "axis": "JP", "val_a": "J", "val_b": "P",
        "img_a": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=800&q=80"
    },
    {
        "q": "여행이나 해외 출장을 준비할 때 숙소와 동선을 짜는 방식은?", 
        "options": ["분단위로 방문할 곳과 맛집을 철저히 조사하고 예약해야 마음이 놓인다.", "대략적인 항공권과 숙소만 잡고 현지에서 끌리는 대로 즉흥적으로 움직인다."], 
        "axis": "JP", "val_a": "J", "val_b": "P",
        "img_a": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=80",
        "img_b": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=800&q=80"
    }
]

# ==========================================
# 3. 세션 상태 관리
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = 0

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.markdown("<h1 class='main-title'>🌐 무역 직무 MBTI 진단 센터</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1.1rem;'>제시된 두 가지 상황 사진과 설명을 보고, 본인에게 더 끌리는 쪽의 <strong>[선택하기]</strong> 버튼을 클릭하세요.</p>", unsafe_allow_html=True)
st.markdown("---")

total_questions = len(QUESTIONS)

if st.session_state.step < total_questions:
    current_idx = st.session_state.step
    item = QUESTIONS[current_idx]

    progress_val = (current_idx + 1) / total_questions
    st.progress(progress_val)
    st.markdown(f"**진행 상황: {current_idx + 1} / {total_questions} 문항**")
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    st.markdown(f"### Q{current_idx + 1}. {item['q']}")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    col_opt1, col_opt2 = st.columns(2, gap="medium")

    with col_opt1:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.image(item["img_a"], use_container_width=True)
        st.markdown(f"<p style='font-size: 1rem; font-weight: 500; min-height: 50px; margin-top: 10px;'>{item['options'][0]}</p>", unsafe_allow_html=True)
        if st.button("👉 이 상황 선택하기 (A)", key=f"btn_a_{current_idx}", use_container_width=True, type="primary"):
            st.session_state.user_answers[item["axis"]] = st.session_state.user_answers.get(item["axis"], []) + [item["val_a"]]
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_opt2:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.image(item["img_b"], use_container_width=True)
        st.markdown(f"<p style='font-size: 1rem; font-weight: 500; min-height: 50px; margin-top: 10px;'>{item['options'][1]}</p>", unsafe_allow_html=True)
        if st.button("👉 이 상황 선택하기 (B)", key=f"btn_b_{current_idx}", use_container_width=True, type="primary"):
            st.session_state.user_answers[item["axis"]] = st.session_state.user_answers.get(item["axis"], []) + [item["val_b"]]
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 5. 결과 분석 및 출력 화면
# ==========================================
else:
    user_answers = st.session_state.user_answers

    def get_counts(axis_key, opt1, opt2):
        lst = user_answers.get(axis_key, [])
        return lst.count(opt1), lst.count(opt2)

    e_cnt, i_cnt = get_counts("EI", "E", "I")
    s_cnt, n_cnt = get_counts("SN", "S", "N")
    t_cnt, f_cnt = get_counts("TF", "T", "F")
    j_cnt, p_cnt = get_counts("JP", "J", "P")

    mbti_e_i = "E" if e_cnt >= i_cnt else "I"
    mbti_s_n = "S" if s_cnt >= n_cnt else "N"
    mbti_t_f = "T" if t_cnt >= f_cnt else "F"
    mbti_j_p = "J" if j_cnt >= p_cnt else "P"

    raw_mbti = f"{mbti_e_i}{mbti_s_n}{mbti_t_f}{mbti_j_p}"
    result_info = JOB_DESCRIPTIONS[raw_mbti]

    st.balloons()

    res_col1, res_col2 = st.columns([1, 1], gap="large")
    
    with res_col1:
        st.markdown(f"""
            <div class="result-box">
                <p style="font-size: 1.1rem; margin-bottom: 0px; opacity: 0.9;">당신의 분석된 정밀 성향 유형</p>
                <h1 style="font-size: 3rem; font-weight: 700; margin: 10px 0px;">{raw_mbti}</h1>
                <hr style="border-color: rgba(255,255,255,0.2); margin: 15px 0px;">
                <p style="font-size: 1.3rem; font-weight: 500; margin-bottom: 0px;">추천 직무: {result_info['job']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("### 🛠️ 핵심 요구 역량")
        skill_cols = st.columns(len(result_info["skills"]))
        for idx, skill in enumerate(result_info["skills"]):
            with skill_cols[idx]:
                st.markdown(f"<div style='background-color: #EFF6FF; color: #1E40AF; padding: 10px; border-radius: 8px; text-align: center; font-weight: 600;'>{skill}</div>", unsafe_allow_html=True)

    with res_col2:
        st.image(result_info["image"], use_container_width=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📝 직무 상세 가이드")
    st.info(result_info["desc"])

    st.markdown("### 🔗 성향과 업무의 연결성 (Synergy & Fit)")
    st.markdown(f"""
        <div class="fit-box">
            <p style="font-size: 1.05rem; color: #334155; line-height: 1.6; margin-bottom: 0px;">
                {result_info['connection']}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 MBTI 축별 상세 응답 분포")

    chart_data = pd.DataFrame({
        "성향 축": ["외향 (E)", "내향 (I)", "감각 (S)", "직관 (N)", "사고 (T)", "감정 (F)", "판단 (J)", "인식 (P)"],
        "점수": [e_cnt, i_cnt, s_cnt, n_cnt, t_cnt, f_cnt, j_cnt, p_cnt],
        "분류": ["에너지", "에너지", "인식", "인식", "판단", "판단", "생활양식", "생활양식"]
    })

    fig = px.bar(
        chart_data, 
        x="성향 축", 
        y="점수", 
        color="분류", 
        text="점수",
        color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
    )
    
    fig.update_traces(textposition='outside', marker_line_width=0, opacity=0.9)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 7], showgrid=True, gridcolor="#E2E8F0"),
        xaxis=dict(showgrid=False),
        font=dict(family="Noto Sans KR", size=13),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 진단 다시 하기", use_container_width=True):
        st.session_state.step = 0
        st.session_state.user_answers = {}
        st.rerun()