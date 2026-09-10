# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩 방법 ("utf-8-sig", "cp949", "euc-kr") 순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 막대그래프 생성 후 그림으로 저장  chart.png
# 실행 streamlit run 0907_3.py


# csv_path = os.path.join(os.path.dirname(_file_), "..", "common", "raw_trade_data.csv")
# csv_path = ",,\common\Titanic.csv"

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager


st.title("인코딩 자동 감지 + 한글 폰트 막대그래프 (Titanic연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 일고, 객실 등급별 생존율을 그래프로 그리기")

csv_path = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
font_path = os.path.join(os.path.dirname(__file__), "SUIT-Bold.otf")



def load_csv_with_encodings(
    file_source,
    encodings: list = ["utf-8-sig", "utf-8", "cp949", "euc-kr"],
) -> pd.DataFrame:
    """여러 인코딩 방식을 순서대로 시도하여 CSV 파일을 불러오는 함수

    :param file_source: 파일 경로 문자열 또는 st.file_uploader로 업로드된 파일 객체
    :param encodings: 시도할 인코딩 목록
    :return: 불러오기에 성공한 pd.DataFrame
    """
    for encoding in encodings:
        try:
            # Streamlit UploadedFile 객체인 경우 파일 포인터를 맨 앞으로 초기화
            if hasattr(file_source, "seek"):
                file_source.seek(0)

            df = pd.read_csv(file_source, encoding=encoding)
            # 성공 시 어떤 인코딩으로 열렸는지 표시 (선택 사항)
            # st.toast(f"'{encoding}' 인코딩으로 불러오기 성공!")
            # plt.rcParams["font.family"] = font_prop.get_name()
            st.write(f"{encoding}으로 읽었습니다.")
            return df
        except (UnicodeDecodeError, LookupError):
            continue

    # 모든 인코딩 실패 시 에러 발생
    raise UnicodeDecodeError(
        f"지정된 인코딩({encodings})으로 파일을 읽을 수 없습니다."
    )


# 인코딩 자동 감지로 csv읽기
st.subheader("1) 인코딩 자동 감지")

df = load_csv_with_encodings(csv_path)
st.markdown("---")
# 갤실등급(Pclass) 별 생존율 집계
# Survived사망0 / 생존1 등급별 평균을 내면
# 그대로가 등급의 생존 비율이 된다.
# 10명 남3 여자7
# 1000 생존300    300/1000    30%
pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
st.dataframe((pclass_survival_rate*100).round(1).rename("생존율(%)"))

# df_df = st.dataframe((pclass_survival_rate*100).round(1).rename("생존율(%)"))
# st.write(df_df)


st.markdown("---")
# 차트 그리기
st.subheader("2) 객실 등급별 생존율 막대그래프")
try :

    # 폰트 파일이 없으면 FileNotFoundError 가 발생
    font_prop = font_manager.FontProperties(fname=font_path)
    # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
    font_manager.fontManager.addfont(font_path)
    st.write("SUIT-Bold 폰트를 적용했습니다.")
except FileNotFoundError : 
    st.warning("SUIT-Bold 폰트 파일을 찾을 수가 없습니다.")

fig, ax = plt.subplots(figsize=(8,5))
(pclass_survival_rate*100).plot(kind="bar", color="blue", ax=ax)
ax.set_title("객실 등급별 생존율", fontproperties=font_prop)
ax.set_xlabel("객실등급(Pclass)", fontproperties=font_prop)
ax.set_ylabel("생존율(%)", fontproperties=font_prop)

for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)
# for > 폰트 강제 인식

st.pyplot(fig)

output_path = os.path.join(os.path.dirname(__file__), "chart.png")
fig.savefig(output_path)









