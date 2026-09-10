"""
스마트 시티 교통 및 도시 이동성 데이터셋
pandas head/tail/shape/info/columns 를 사용해서 데이터셋의 기본 정보를
화면에 순서대로 보여주는 streamlit 앱이다.
실행방법 streamlit run 0907_2.py
"""

import pandas as pd #엑셀
import streamlit as st
import io


st.title("🏬🏬스마트 시티 교통 및 도시 이동성 데이터셋🏬")
#화면 맨 위에 "🏬 스마트 시티 교통 일기장"이라고 큼직한 간판과 설명을 걸어줘요.
st.caption("pandas의 head/tail/shape/info/columns으로 데이터셋 기본 정보를 확인합니다.")

csv_path = "smart_city_traffic_mobility.csv"

upload_file = st.file_uploader("smart_city_traffic_mobility 파일을 직접 업로드 할 수 있습니다.(선택사항)", type="csv")
# "내가 가진 파일이 있으면 여기 서랍에 넣어줘!" 하고 파일 올리는 상자를 만들어요.

if upload_file is not None :
    df = pd.read_csv(upload_file)
else :
    try :
        df = pd.read_csv(csv_path)
    except FileNotFoundError : 
        st.error("❌스마트 시티 교통 및 도시 이동성 데이터셋 파일을 찾을수가 없습니다.")
        st.info("같은 경로에 파일을 업로드 하거나 csv파일을 폴더에 넣고 새로고침하세요")
        df = None   
# 서랍에 새 파일을 넣었으면 그걸 먼저 읽고, 안 넣었으면 컴퓨터에 원래 있던 기본 파일을 꺼내와요.
# 둘 다 없으면 "파일을 못 찾겠어요!" 하고 빨간 경고창을 띄워요.

if df is not None : 
    st.subheader("1) head() : 데이터의 앞부분 5개 행 미리보기")
    st.dataframe(df.head(), use_container_width=True) # 기본행 5개
    # 두꺼운 책의 맨 앞 5쪽만 먼저 살짝 넘겨보는 거예요.
    # 어떤 내용이 적혀 있는지 맛보기로 구경해요.

    st.subheader("2) tail() : 데이터의 뒷부분 5개 행 미리보기")
    st.dataframe(df.tail(), use_container_width=True) # 기본행 5개
    # 책의 맨 뒷부분 5쪽을 펼쳐보는 거예요.
    # 맨 마지막에는 어떤 내용으로 끝나는지 확인해요.

    st.subheader("3) shape() : 행개수, 열개수")
    col1, col2 = st.columns(2)
    with col1 :
        st.metric("행 개수", f"{df.shape[0]}개")
    with col2 :
        st.metric("열 개수", f"{df.shape[1]}개")
        # 이 표가 가로로 몇 줄, 세로로 몇 칸인지 세어줘요.
        # "사람이 1,000명 적혀 있고(행 개수), 적힌 질문은 10개구나!(열 개수)"
        # 하고 표의 전체 크기를 한눈에 보여줘요.

    st.subheader("4) columns : 전체 열(컬럼) 이름 목록")
    st.write(list(df.columns))
    # 표 맨 윗줄에 적힌 제목들
    # (예: 버스 번호, 출발 시간, 도착지)만 쏙 뽑아서 이름표 목록을 읽어줘요.

    st.subheader("5) info() : 각 열의 자료형과 결측치(NaN) 여부 요약")
 
    buffer = io.StringIO()
    df.info(buf=buffer)
    # 빈칸(숙제 빼먹은 곳)이 있는지, 글자가 적혀 있는지 숫자가 적혀 있는지 표 전체의
    # 건강 상태를 요약한 리포트를 뽑아서 보여줘요.
    # 원래는 컴퓨터 까만 창 뒤에 몰래 적히는 리포트인데, io.StringIO()라는
    # 임시 메모장에 받아 적은 다음 우리 눈에 보이게 화면에 띄워줘요.
    st.text(buffer.getvalue())


    st.success("기초 정보 확인 끝났습니다. 다음 예제에서 전처리 필터링을 할께요")
    # "검사 끝! 참 잘했어요!" 하고 초록색 알림창을 띄우며 마무리를 지어요.