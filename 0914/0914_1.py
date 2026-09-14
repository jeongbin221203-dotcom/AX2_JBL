import os
import webbrowser
import folium

# 1. 서울 시내 명소 4곳 샘플 데이터
places = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "N서울타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.5665, "lon": 127.0092},
    {"name": "롯데월드타워", "lat": 37.5126, "lon": 127.1025},
]

# 2. Esri 타일을 적용하여 OSM 403 차단 회피
seoul_center = [37.5796, 126.9770]
map = folium.Map(
    location=seoul_center,
    zoom_start=13,
    tiles="CartoDB positron",  # 고배율 줌 완벽 지원
    max_zoom=19,  # 최대 확대 한도 지정
)

# 3. 지도 위에 마커 추가
for place in places:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=place["name"],
        popup=folium.Popup(place["name"], max_width=200),
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(map)

# 4. 파일 저장 및 브라우저에서 자동 실행
current_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(current_dir, "basic_map.html")

map.save(save_path)
print(f"지도 파일이 성공적으로 저장되었습니다: {save_path}")

# 코드를 실행하면 웹 브라우저에서 지도가 자동으로 열립니다.
webbrowser.open(save_path)