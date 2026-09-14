# 대화 기록을 기억하는 멀티턴 챗봇(스트리밍 응답)
# st.session_state에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 Streamlit의 채팅 전용 위젯을 사용합니다.
# Stream=true 옵션으로 답변이 실시간으로 타이핑되듯 출력됩니다.
# streamlit.run 0911_3.py

# 시스템 메시지를 사용자가 설정 하도록
# 대화 기록 초기화 버튼



# 대화 기록을 기억하는 멀티턴 챗봇 (스트리밍 응답)
# 실행 명령어: streamlit run 0911_3.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="멀티턴 대화형 챗봇", page_icon="💬", layout="wide")

st.title("예제2) 대화 기록을 기억하는 챗봇")
st.caption("이전 대화 맥락을 기억하며 실시간 타이핑 효과(스트리밍)로 응답하는 챗봇입니다.")

# ---------------------사이드바 설정-----------------------

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="sk-로 시작하는 API Key를 입력하세요",
    )
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)

    # 1. 사용자가 직접 지정하는 시스템 프롬프트
    system_prompt = st.text_area(
        "시스템 메시지 (봇의 역할/성격)",
        value="당신은 친절하고 유능한 AI 어시스턴트입니다.",
        height=100,
    )

    st.markdown("[API 키 발급받기](https://platform.openai.com/api-keys)")
    st.divider()

    # 2. 대화 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------세션 상태 초기화-----------------------

# st.session_state에 대화 기록 저장소 생성
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------이전 대화 기록 렌더링-----------------------

# 화면이 리로드되어도 기존 메시지들을 순서대로 화면에 다시 그려줌
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------사용자 입력 및 스트리밍 처리-----------------------

# st.chat_input: 화면 하단에 고정되는 채팅 전용 입력창
if user_input := st.chat_input("메시지를 입력하세요..."):
    if not api_key:
        st.error("오른쪽 사이드바에서 OpenAI API Key를 먼저 입력해 주세요.")
    else:
        # 1. 사용자 입력을 세션 기록에 추가하고 화면에 렌더링
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. API 전송용 메시지 조립 (시스템 메시지 + 이전 대화 누적 기록)
        api_messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # 3. 어시스턴트 응답 스트리밍 출력
        with st.chat_message("assistant"):
            try:
                client = OpenAI(api_key=api_key)

                # stream=True 옵션 지정
                stream = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    stream=True,
                )

                # st.write_stream을 통해 한 글자씩 실시간 타이핑 효과 출력
                full_response = st.write_stream(stream)

                # 4. 완료된 AI 답변을 대화 기록에 저장
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")