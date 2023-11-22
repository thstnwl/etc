# 도로명주소와 지번주소로 경도와 위도 찾기 (V-World API)
import pandas as pd
import requests

# DataFrame 로드
df = pd.read_excel('path/file_name.xlsx')

url = 'http://api.vworld.kr/req/address?'
params = 'service=address&request=getcoord&version=2.0&crs=epsg:4326&refine=true&simple=false&format=json&type='
road_type1 = 'ROAD'     # 도로명 주소
road_type2 = 'PARCEL'   # 지번 주소
address = '&address='
keys = '&key='
api_key = 'V-World API 키' 

def request_geo(road, address_type):
    page = requests.get(url + params + address_type + address + road + keys + api_key)
    json_data = page.json()
    if json_data['response']['status'] == 'OK':
        x = json_data['response']['result']['point']['x']
        y = json_data['response']['result']['point']['y']
        #print(road, x, y)
        return x, y
    else:
        print(road, "변환 불가")
        return None

# DataFrame의 각 행에 대해 '소재지도로명주소'('소재지지번주소')로 위/경도 찾기
for index, row in df.iterrows():
    if pd.isna(row['소재지도로명주소']):
        result = request_geo(row['소재지도로명주소'], road_type1)
    else:
        result = request_geo(row['소재지지번주소'], road_type2)

    # 진행 현황
    if index % 50 == 0:
        print(index)
    
    if result:
        df.at[index, '위도'] = result[0]
        df.at[index, '경도'] = result[1]

# 결과 저장
df.to_excel('path/file_name.xlsx', index=False)
