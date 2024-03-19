import random
import requests

from bs4 import BeautifulSoup

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('mongodb://admin:admin@43.200.7.212', 22)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle                      # 'dbjungle'라는 이름의 db를 만듭니다.



def insert_all():
    # URL을 읽어서 HTML를 받아오고,
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://search.daum.net/search?w=tot&m=&q=2022%EB%85%84%20%EC%98%81%ED%99%94%20%EC%88%9C%EC%9C%84&nzq=%EC%9D%BC%EA%B0%84%EC%98%81%ED%99%94%EC%88%9C%EC%9C%84&DA=NSJ', headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup = BeautifulSoup(data.text, 'html.parser')

    # select를 이용해서, li들을 불러오기
    movies = soup.select('#morColl > div.coll_cont > div > ol > li')
    print(len(movies))


    # movies (li들) 의 반복문을 돌리기
    for movie in movies:
        # movie 안에 a 가 있으면,
        # (조건을 만족하는 첫 번째 요소, 없으면 None을 반환한다.)
        tag_element = movie.select_one('div.wrap_cont > div.info_tit > a')
        if not tag_element:
            continue
        title = tag_element.text  # a 태그 사이의 텍스트를 가져오기
        # print(title)

        tag_element = movie.select_one('div.wrap_cont > dl:nth-child(3) > dd')
        if not tag_element:
            continue
        open_date = tag_element.text[:-1]
        # print(open_date)

        # 년도.월.일 형태에서 년도, 월, 일을 추출하기
        # (각각이 . 으로 구분되어있으므로 . 을 기준으로 split 한 뒤 각각을 문자형태에서 숫자형태로 변경해준다.)
        # if open_date[-1:] == '.' and len(open_date) > 10:
        #     (open_year, open_month, open_day) = [int(element) for element in open_date[0:-1].split('.')]
        # else:
        #     open_year = 2024
        #     open_month = 99
        #     open_day = 99
        #     # print(open_year, open_month, open_day)

        # 개봉년도를 "22" 가 아니라 "2022" 형태로 바꾸기 위해서 2000 을 더해준다.
        # open_year += 2000

        # 누적 관객수를 얻어낸다. "783,567명" 과 같은 형태가 된다.
        tag_element = movie.select_one('div.wrap_cont > dl:nth-child(5) > dd')
        if not tag_element and str(tag_element)[-1:] == '명':
            continue
        viewers = tag_element.findChild(string=True, recursive=False)
        viewers = int(''.join([c for c in viewers if c.isdigit()]))
        # print(viewers)

        # 영화 포스터 이미지 URL 을 추출한다.
        tag_element = movie.select_one('div.wrap_thumb > a > img')
        if not tag_element:
            continue
        # print(tag_element)
        poster_url = tag_element['data-original-src']
        if not poster_url:
            continue
        # print(poster_url)


        # 존재하지 않는 영화인 경우만 추가한다.
        found = list(db.movies.find({'title': title}))
        if found:
            continue

        # 좋아요를 random 으로 정한다 [0, 100)
        likes = random.randrange(0, 100)

        doc = { 
            'title': title,
            # 'open_year': open_year,
            # 'open_month': open_month,
            # 'open_day': open_day,
            'open_date': open_date,
            'viewers': viewers,
            'poster_url': poster_url,
            # 'info_url': info_url,
            'likes': likes,
            'trashed': False,
        }   
        db.movies.insert_one(doc)
        print('완료: ', title, open_date, viewers, poster_url, likes)


if __name__ == '__main__':
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    insert_all()
