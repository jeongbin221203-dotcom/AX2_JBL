# lotto v1
# lotto v2


from datetime import datetime
import random
import streamlit as st

st.title("🎱 로또 번호 자동 생성기")
st.caption(
    "버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다."
)


# ==============================================================================
# [1] 1세트 번호 생성 함수
# ==============================================================================
def lotto_one_set() -> list:
    """1~45 사이에서 중복 없이 6개를 뽑아 오름차순 정렬된 리스트로 반환"""
    numbers = set()  # 빈 집합(set) 생성
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(numbers)


# ==============================================================================
# [2] 로또 번호대별 색상 공 HTML 생성 함수
# ==============================================================================
def get_lotto_ball_html(number: int) -> str:
    """공식 로또 색상 규칙에 맞춘 동그란 공 스타일 HTML 태그 생성"""
    if number <= 10:
        bg_color = "#fbc400"  # 노란색 (1~10)
        text_color = "#000000"
    elif number <= 20:
        bg_color = "#69c8f2"  # 파란색 (11~20)
        text_color = "#ffffff"
    elif number <= 30:
        bg_color = "#ff7272"  # 빨간색 (21~30)
        text_color = "#ffffff"
    elif number <= 40:
        bg_color = "#aaaaaa"  # 회색 (31~40)
        text_color = "#ffffff"
    else:
        bg_color = "#b0d840"  # 초록색 (41~45)
        text_color = "#ffffff"

    # 원형 배지 CSS 인라인 스타일
    ball_style = f"""
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background-color: {bg_color};
        color: {text_color};
        font-weight: bold;
        font-size: 15px;
        margin-right: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.25);
    """
    # border-radius: 50% : 네모 박스를 완벽한 동그라미로 깎아줍니다.
    # width: 38px; height: 38px; : 지름 38픽셀 크기의 공을 만듭니다.
    # box-shadow : 공 아래쪽에 살짝 그림자를 넣어 입체감을 줍니다.
    return f'<span style="{ball_style}">{number}</span>'
    # 완성된 동그란 공 디자인 태그를 반환합니다.

st.markdown("---")

# ==============================================================================
# [3] 버튼 및 생성 결과 화면 출력
# ==============================================================================
# 버튼 클릭 상태를 변수에 저장
btn_clicked = st.button("5세트 번호 생성하기", key="lotto_generate_btn")

# 버튼을 눌렀을 때만 번호를 새로 뽑도록 설정 (선택 사항)
if btn_clicked:
    # 날짜 포맷: %Y(연도), %m(월), %d(일), %H(시), %M(분), %S(초)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"생성 시간 : **{now_str}**")
    st.markdown("<br>", unsafe_allow_html=True)

    for set_index in range(1, 6): #총 5번 반복해서 5세트를 만듭니다.
        lotto_nums = lotto_one_set() #실행해 번호 6개를 뽑습니다.

        # 6개 숫자를 각각 공 HTML 태그로 변환 후 이어붙이기
        balls_html = "".join([get_lotto_ball_html(num) for num in lotto_nums])
        # 6개 번호를 각각 예쁜 색상 공으로 바꾼 뒤 한 줄로 묶습니다.

        # 세트 레이블과 공 뱃지 렌더링
        row_html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: bold; font-size: 16px; width: 80px;">{set_index}세트 :</span>
            <div>{balls_html}</div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
        # "1세트 : [공6개]" 모양을 웹 화면에 깔끔하게 보여줍니다.
else:
    st.info("상단의 **'5세트 번호 생성하기'** 버튼을 클릭해 보세요.")
