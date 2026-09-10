##print("안녕하세요")
#python 0903.py / cd.. / cd AX2_JBL

#conda create -n myenv python=3.10  > y / conda list
#conda activate myenv (활성화)
#conda deactivate (비활성화) / conda remove -n myenv (삭제) > y  (--all)
##import pandas as pd

#pip install pandas (개별입력)
import streamlit as st
##requirements.txt (통합입력 pandas, streamlit)
#pip install -r requirements.txt (통합입력)


# streamlit run 0903.py
#(myenv) C:\Users\user\AX2_JBL>streamlit run .\0903\0903.py
#cd C:\Users\user\AX2_JBL\0903



# st.title("내용") 은 페이지에서 가장 크고 굵은 제목을 만든다(h1 느낌)
st.title("무역데이터 부트캠프 자기소개")
# st.header("내용")은 title보다 한단계 작은 큰 제목(h2 느낌)
st.header("안녕하세요! Streamlit으로 만든 첫 페이지 입니다.👍")
# st.subheader("내용")은 header보다는 한단계 작은 큰 제목(h3 느낌)
st.subheader("오늘 배운 것 : 텍스트를 화면에 예쁘게 보여주는 방법")
# st.text("내용") 꾸밈이 전혀 없는 순수 텍스트를 그대로 출력
st.text("st.text로 출력한 문장입니다, 줄을 바꾸거나 굵기 등이 서식에 적용되지 않는다.")
# st.caption("내용") 아주 작은 글씨로 보조 설명을 넣을떄
st.caption("이 문장은 st.caption으로 작성한 작은 보조 설명")
#st.markdown("") """ 마크다운 문법 """ shift + alt + a
#st.markdown("---") 마크다운 문법 (굵기, 기울임, 링크, 목록)
st.markdown(
    """
    ### 😊마크다운으로 작성한 자기소개
    - **이름** : 이정빈
    - **관심분야** : *데이터분석*, 무역데이터 시각화
    - **목표** : 나만의 데시보드 만들기
    - 참고 링크 : [네이버](https://www.naver.com)
"""
)

st.markdown("---")
st.subheader("오늘 배운 한줄 코드")
st.code(
    """
    st.title("hello Steamlit!")
    st.title("hello Steamlit!)
"""
)