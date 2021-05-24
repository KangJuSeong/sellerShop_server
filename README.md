## 쇼핑몰별 판매 현황 대쉬보드 (Intern)

### 1. 개발 목적
* 많은 쇼핑몰에서 같은 판매자들이 동일한 물품을 판매하고 있고, 판매 현황 관리를 위해서 각각의 쇼핑몰을 번거롭게 로그인하고 확인해야 함.
* 이러한 문제를 해결하기 위해 등록해놓은 쇼핑몰에 대한 판매 현황을 크롤링한 후 어플에서 한 눈에 확인 할 수 있도록 하여 효율적으로 판매 관리를 할 수 있음.

### 2. 개발 스택 및 도구
`Django`
`Selenium`
`PostMan`

### 3. 맡은 역할
* 쇼핑몰 별 판매 물품 현황 크롤링 모듈 만들기.
* 유저 및 쇼핑몰 유저 정보 모델링.
* 로그인, 회원가입, 리뷰, 구독 API 작성.
* 크롤링 한 데이터를 클라이언트로 보내주는 API 작성.

### 4. 모델 설계
* Django 에서 제공되는 SQLite3 를 이용
* ERD 다이어그램   
![](D:\sellerShop_server\img\erd.png)
  
> 테이블별 상세 내용    
> 1. User
>   * 기본적으로 제공하는 Django AbstractUser 모델을 상속.
>   * 추가로 필요한 전화번호 phone
> 2. Review
>   * 리뷰 작성시 유저를 FK로 하는 user
>   * 작성 시기, 평점, 리뷰를 저장하는 write_at, grade, review
> 3. SubscriptionLog
>   * 유저의 구독 여부와 시작 날짜와 종료 날짜를 저장하는 flag, start_at, end_at
>   * 유저를 FK로 하는 user
> 4. ShipAccountInfo
>   * 쇼핑몰의 종류를 체크하는 shop
>   * 해당 쇼핑몰의 ID, PW를 저장하는 login_id, login_pw
>   * 로그인 시 만들어진 세션을 저장하는 session
>   * 해당 유저를 외래키로 하는 user






