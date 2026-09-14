# 예제3) 파일 업로드 문서 요약 앱
# 실행 명령어: streamlit run 0911_4.py

import io
from openai import OpenAI
import pypdf
import streamlit as st

st.set_page_config(page_title="문서 요약 AI", page_icon="📄", layout="wide")

st.title("예제3) 스마트 문서 요약기")
st.caption("문서를 업로드하고 원하는 분량과 스타일에 맞춰 AI 요약을 생성하세요.")

# ---------------------사이드바 설정-----------------------

with st.sidebar:
    st.header("⚙️ 설정 및 옵션")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="sk-로 시작하는 API Key를 입력하세요",
    )
    # gpt-4.1-mini 유지
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)

    st.divider()
    st.subheader("📝 요약 옵션")

    # 3. 요약 길이 옵션
    length_option = st.radio(
        "요약 길이",
        ["짧게 (3줄)", "보통 (7줄)", "자세히 (상세 분석)"],
        index=0,
    )

    # 4. 요약 스타일 옵션
    style_option = st.selectbox(
        "요약 스타일",
        [
            "일반 (친근하고 쉬운 설명)",
            "고급 (명확하고 정제된 비즈니스 보고서)",
            "전문가 (전문 용어 및 학술/분석 중심)",
        ],
        index=0,
    )

    st.divider()
    st.markdown("[API 키 발급받기](https://platform.openai.com/api-keys)")


# ---------------------문서 텍스트 추출 함수-----------------------

def extract_text(file) -> str:
    """업로드된 파일의 확장자에 맞춰 텍스트를 추출하는 함수"""
    file.seek(0)
    if file.name.endswith(".txt") or file.name.endswith(".md"):
        return file.read().decode("utf-8", errors="ignore")
    elif file.name.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(file.read()))
        extracted = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(extracted).strip()
    return ""


# ---------------------메인 화면: 업로드 및 미리보기-----------------------

uploaded_file = st.file_uploader(
    "요약할 문서를 업로드하세요", type=["txt", "md", "pdf"]
)

if uploaded_file:
    # 텍스트 추출
    document_text = extract_text(uploaded_file)

    if not document_text:
        st.warning("문서에서 텍스트를 읽어올 수 없습니다. 다른 파일을 시도해 주세요.")
    else:
        # 1. 업로드한 문서 미리보기
        st.subheader("👀 문서 내용 미리보기")
        preview_text = document_text[:1500] + (
            "..." if len(document_text) > 1500 else ""
        )
        st.text_area("미리보기 (최대 1,500자)", preview_text, height=200, disabled=True)
        st.caption(f"전체 글자 수: 약 {len(document_text):,}자")

        # 2. 요약하기 버튼
        if st.button("✨ 요약하기", type="primary"):
            if not api_key:
                st.error("사이드바에 OpenAI API Key를 먼저 입력해주세요.")
            else:
                # 프롬프트 조건 생성
                system_instruction = f"""
                당신은 전문 문서 요약 어시스턴트입니다. 다음 조건을 반드시 지켜 요약하세요:
                - 길이 조건: {length_option}
                - 스타일 조건: {style_option}
                - 사실에 기반하여 원문의 핵심을 누락 없이 정리하세요.
                """

                try:
                    client = OpenAI(api_key=api_key)

                    with st.spinner("문서를 분석하여 요약 중입니다..."):
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {
                                    "role": "user",
                                    "content": f"다음 문서를 요약해 줘:\n\n{document_text}",
                                },
                            ],
                        )

                    summary_result = response.choices[0].message.content

                    # 요약 결과 출력
                    st.divider()
                    st.subheader("📌 요약 결과")
                    st.markdown(summary_result)

                    # 토큰 사용량 안내
                    usage = response.usage
                    st.caption(
                        f"소모 토큰: 입력 {usage.prompt_tokens}개 | 출력 {usage.completion_tokens}개 | 총합 {usage.total_tokens}개"
                    )

                except Exception as e:
                    st.error(f"요약 중 오류가 발생했습니다: {e}")

# 사이드바에 API Key가 입력되지 않은 경우 메인 화면 최하단에 상시 안내
if not api_key:
    st.info("💡 사이드바에 OpenAI API Key를 먼저 입력해주세요.")