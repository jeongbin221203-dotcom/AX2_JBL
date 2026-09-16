import pandas as pd
import requests
from bs4 import BeautifulSoup

# 삼성전자 종목코드: 005930
code = "005930"
stock_name = "삼성전자"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

data_list = []

# 최근 1~3페이지(약 30거래일) 데이터 수집 (원하는 범위로 조절 가능)
for page in range(1, 4):
    url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
    res = requests.get(url, headers=headers)
    res.encoding = "cp949"

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table.type2 tr")

    for tr in rows:
        tds = tr.select("td")
        # 날짜와 수치가 온전히 들어있는 행(td가 7개)만 추출
        if len(tds) >= 7 and tds[0].get_text(strip=True):
            date = tds[0].get_text(strip=True)
            close_price = tds[1].get_text(strip=True).replace(",", "")
            
            # 전일 대비 등락 기호 처리 (상승/하락)
            diff_text = tds[2].get_text(strip=True).replace(",", "")
            ico_elem = tds[2].select_one("img")
            if ico_elem and "상승" in ico_elem.get("alt", ""):
                diff_val = f"+{diff_text}"
            elif ico_elem and "하락" in ico_elem.get("alt", ""):
                diff_val = f"-{diff_text}"
            else:
                diff_val = diff_text

            market_open = tds[3].get_text(strip=True).replace(",", "")
            high_price = tds[4].get_text(strip=True).replace(",", "")
            low_price = tds[5].get_text(strip=True).replace(",", "")
            volume = tds[6].get_text(strip=True).replace(",", "")

            data_list.append([
                date,
                int(close_price),
                diff_val,
                int(market_open),
                int(high_price),
                int(low_price),
                int(volume),
            ])

# 데이터프레임 생성
columns = ["날짜", "종가(현재가)", "전일대비", "시가", "고가", "저가", "거래량"]
df = pd.DataFrame(data_list, columns=columns)

# 엑셀 파일로 저장
excel_filename = f"{stock_name}_{code}_시세.xlsx"
df.to_excel(excel_filename, index=False, engine="openpyxl")

print("=" * 50)
print(f"📊 [{stock_name} ({code})] 시세 데이터 수집 완료")
print(f"총 {len(df)}건의 일별 거래 데이터가 '{excel_filename}' 파일로 저장되었습니다.")
print("=" * 50)
print(df.head())  # 상위 5건 미리보기