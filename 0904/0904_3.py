# random 모듈을 이용해서 1~45중 중복 없는 번호 6개를 뽑고
# 자료 구조 list, set(중복안됨) 버튼을 누르면 5세트를 한번에 생성
# datetime 으로 생성시간도 함께 보여준다.

import streamlit as st
import random
from datetime import datetime

st.title("🎱로또 번호 자동 생성기")
st.caption("버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.")


# while 조건식 :
#         참 처리문
# return 조건식

def lotto_one_set() -> list :
    """ 1~45 에서 중복  없이 번호 6개 뽑아 정렬된 리스트로 반환"""

    number = set[int]()
    while len(number) < 6 :
            number.add(random.randint(1,45)) # 1이상 45이하 정수 하나 뽑기
    return sorted(number)

st.markdown("---")


if st.button("5세트 번호 생성하기", key="lotto_generate_btn"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"생성시간 : **{now_str}**")

    for set_index in range(1,6):
        lotto_num = lotto_one_set()
# [수정 3] 번호 앞에 색상 이모지만 붙여서 기존 st.write 그대로 출력
        colored_nums = []
        for n in lotto_num:
            if n <= 10:
                colored_nums.append(f"🟡 {n}")
            elif n <= 20:
                colored_nums.append(f"🔵 {n}")
            elif n <= 30:
                colored_nums.append(f"🔴 {n}")
            elif n <= 40:
                colored_nums.append(f"⚪ {n}")
            else:
                colored_nums.append(f"🟢 {n}")


        st.write(f"**{set_index}세트** : {' | '.join(colored_nums)}")






# import streamlit as st
# import random

# st.set_page_config(page_title="로또 번호 생성기", page_icon="🎰")

# st.title("🎰 로또 6/45 번호 자동 생성기")

# # 게임 수 선택 (1 ~ 5게임)
# num_games = st.slider("생성할 게임 수를 선택하세요", min_value=1, max_value=5, value=5)

# # 번호 생성 함수
# def generate_lotto():
#     numbers = random.sample(range(1, 46), 6)
#     return sorted(numbers)

# # 생성 버튼
# if st.button("🎲 로또 번호 뽑기!", type="primary"):
#     st.subheader("🎉 오늘의 추천 번호")
    
#     for i in range(num_games):
#         lotto_numbers = generate_lotto()
#         # 번호 포맷팅 (두 자리 맞춤 및 강조)
#         formatted_numbers = "  ".join([f"`{num:02d}`" for num in lotto_numbers])
#         st.write(f"**Game {i + 1}** : {formatted_numbers}")
        
#     st.balloons()  # 축하 풍선 애니메이션 효과