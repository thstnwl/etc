# 도로명주소와 지번주소로 경도와 위도 찾기 (Google Maps Geocoding API)
import pandas as pd
from geopy.geocoders import GoogleV3

# DataFrame 로드
df = pd.read_excel('path/file_name.xlsx')

api_key = "Google Maps Geocoding API 키"

def address_to_coordinates_google_maps(address, api_key):
    geolocator = GoogleV3(api_key=api_key)
    location = geolocator.geocode(address)

    if location:
        latitude, longitude = location.latitude, location.longitude
        #print(address, latitude, longitude)
        return latitude, longitude
    else:
        print(address, "변환 불가")
        return None

# DataFrame의 각 행에 대해 '소재지도로명주소'('소재지지번주소')로 위/경도 찾기
for index, row in df.iterrows():
    if pd.notna(row['소재지도로명주소']):
        result = address_to_coordinates_google_maps(row['소재지도로명주소'], api_key)
    else:
        result = address_to_coordinates_google_maps(row['소재지지번주소'], api_key)

    # 진행 현황
    if index % 50 == 0:
        print(index)
    
    if result:
        df.at[index, '위도'] = result[0]
        df.at[index, '경도'] = result[1]

# 결과 저장
df.to_excel('path/file_name.xlsx', index=False)