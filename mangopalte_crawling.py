
# -*- coding: utf-8 -*-

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import time

# 크롬 드라이버 경로
driver_path = "/opt/homebrew/bin/chromedriver"

# 크롤링할 사이트 주소를 정의합니다.
source_url = "https://www.mangoplate.com/search/노원구?keyword=노원구&page=55"

# Selenium 설정
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-local-proxy')

# 브라우저 열기
driver = webdriver.Chrome(service=service, options=options)
driver.get(source_url)
time.sleep(5)
req = driver.page_source
soup = BeautifulSoup(req, "html.parser")
info_list = soup.find_all(name="div", attrs={"class":"info"})

# 페이지 URL 추출
page_urls = []
page_url_base = "https://www.mangoplate.com"
for index in range(len(info_list)):
    info = info_list[index]
    review_url = info.find(name="a")
    if review_url is not None:
        page_urls.append(page_url_base + review_url.get("href"))

# 중복 URL 제거
page_urls = list(set(page_urls))

# 크롤링에 사용할 빈 리스트 생성
data = []

# 페이지 순회
for page_url in page_urls:
    # 상세보기 페이지에 접속합니다.
    driver.get(page_url)
    time.sleep(5)
    
    # 가게 이름을 가져옵니다.
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    restaurant_name_tag = soup.find(name="h1", attrs={"class":"restaurant_name"})
    restaurant_name = restaurant_name_tag.text if restaurant_name_tag else ""
    
    # 평점을 가져옵니다.
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    score_tag = soup.find(name="strong", attrs={"class": "rate-point"})
    score = score_tag.text.strip() if score_tag else ""
    
    # 평가 정보를 가져옵니다.
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    evaluation_tag = soup.find(name="span", attrs={"class": "restaurant_item"})
    evaluation = evaluation_tag.text.strip() if evaluation_tag else ""
    
    # 리뷰를 크롤링합니다.
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    review_list = soup.find(name="section", attrs={"class": "RestaurantReviewList"})
    
    # 평가 정보('맛있다' 마크)를 가져옵니다.
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    review_recommend_list = review_list.find_all(name="div", attrs={"class": "RestaurantReviewItem__Rating RestaurantReviewItem__Rating--Recommend"})
    
    # 리뷰를 가져옵니다.
    review_text_list = review_list.find_all(name="div", attrs={"class": "RestaurantReviewItem__ReviewContent"})
    
    # 리뷰 텍스트를 합쳐서 하나의 문자열로 만듭니다.
    reviews_combined = " // ".join([review_text.find(name="p").text.strip() for review_text in review_text_list])
    
    # 가게 이름, 평점, 평가 정보, 리뷰를 데이터에 추가합니다.
    data.append([restaurant_name, score, reviews_combined])

# 크롤링에 사용한 브라우저를 종료합니다.
driver.quit()

# 데이터프레임 생성
df = pd.DataFrame(data, columns=["restaurant_name", "score", "reviews"])

# 데이터를 CSV 파일로 저장합니다.
df.to_csv("mangoplate_reviews55.csv", index=False)
print("데이터를 CSV 파일로 저장하였습니다.")
