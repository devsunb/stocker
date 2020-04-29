# stocker

온라인 쇼핑몰 재고 수집기

## 개요

온라인 쇼핑몰의 재고를 자동으로 수집하는 Python 스크립트다.

재고가 발생하면 자동으로 구매하는 기능도 추가하였다.

이걸 만든 이유는 닌텐도 스위치 동물의 숲 에디션을 구하기 위해서였지만 하다보니 이걸로 데이터를 많이 모으면 다음에 온라인 쇼핑몰 시세 분석 같은 거 할 때도 쓸 수 있을 것 같다.

## 사용법

### 설정 파일

설정 파일을 다음과 같이 작성한다.

```yaml
GENERAL:
  DATA_PATH: "<데이터 경로>"
  CHROMEDRIVER:
    PATH: "<chromedriver 경로>"
    TIMEOUT: 10
    WINDOW_SIZE: [1000, 1000]
    OPTION:
      - "headless"
      - "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"
      - "lang=ko_KR"
SITE:
  COUPANG:
    URL:
      BASE: "https://www.coupang.com/"
      PRODUCT: "https://www.coupang.com/vp/products/{}"
    ACCOUNT:
      USER: "<이메일>"
      PASSWORD: "<비밀번호>"
    PAY:
      BANK: "기업은행"
      PASSWORD: [0, 1, 2, 3, 4, 5]
    DATA_PATH:
      SCREENSHOT: "<데이터 경로 하위 상대 경로>"
      REF_KEYPAD: "<데이터 경로 하위 상대 경로>"
OUTPUT:
  INFLUXDB:
    HOST: "<호스트>"
    PORT: 8086
    USER: "<유저>"
    PASSWORD: "<비밀번호>"
    DB: "<DB 이름>"
RECIPE:
  - SITE: "COUPANG"
    PRODUCT_NUMBER: 1384804427
    PRODUCT_NAME: "닌텐도 스위치 동물의 숲 에디션"
    OUTPUT:
      - "INFLUXDB"
    TERM: 10
    TIMEOUT: 0
```

### 실행

다음과 같은 명령어로 실행할 수 있다.

```bash
python3 run.py -l DEBUG -c <설정 파일 경로>
```
