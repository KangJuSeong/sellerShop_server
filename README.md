# 쇼핑몰별 판매 현황 대쉬보드 (Intern)

## 1. 개발 목적
* 많은 쇼핑몰에서 같은 판매자들이 동일한 물품을 판매하고 있고, 판매 현황 관리를 위해서 각각의 쇼핑몰을 번거롭게 로그인하고 확인해야 함.
* 이러한 문제를 해결하기 위해 등록해놓은 쇼핑몰에 대한 판매 현황을 크롤링한 후 어플에서 한 눈에 확인 할 수 있도록 하여 효율적으로 판매 관리를 할 수 있음.

## 2. 개발 스택 및 도구
`Python`
`Django`
`Selenium`
`PostMan`
`Bitbucket`
`Jira`

## 3. 맡은 역할
* 쇼핑몰 별 판매 물품 현황 크롤링 모듈 만들기.
* 유저, 쇼핑몰 유저, 리뷰, 구독, 공지사항 모델링.
* 로그인, 회원가입, 리뷰, 구독, 공지사항 API 작성.
* 크롤링 한 데이터를 클라이언트로 보내주는 API 작성.

## 4. 모델 설계 및 작성
* ERD 다이어그램 
![](https://github.com/KangJuSeong/sellerShop_server/blob/main/erd.png)
  
> 테이블별 상세 내용    
> 1. User
>   * 기본적으로 제공하는 Django AbstractUser 모델을 상속.
>   * 추가로 필요한 전화번호 phone
> 2. Review
>   * 리뷰 작성시 유저를 FK로 하는 user
>   * 작성 시기, 평점, 리뷰를 저장하는 write_at, grade, review
> 3. Notice
>   * 공지사항 제목을 저장하는 title
>   * 공지사항 내용을 저장하는 content
> 4. SubscriptionLog
>   * 유저의 구독 여부와 시작 날짜와 종료 날짜를 저장하는 flag, start_at, end_at
>   * 유저를 FK로 하는 user
> 5. ShipAccountInfo
>   * 쇼핑몰의 종류를 체크하는 shop
>   * 해당 쇼핑몰의 ID, PW를 저장하는 login_id, login_pw
>   * 로그인 시 만들어진 세션을 저장하는 session
>   * 해당 유저를 외래키로 하는 user

## 5. 필요한 모듈 개발

`APIView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/337a439a87aea4579bf588a2d885e23c84ea45d0/shoppingmall_back/utils/views.py#L10-L24)
* `APIView` 클래스는`JsonResponse`를 리턴해주는 클래스 메서드이며 HTTP 통신으로 `Request` 에 대한 `Response` 를 반환해주는 방식.   

`AuthAPIView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/views.py#L27-L41)   
* `AuthAPIView` 클래스는 `Request` 가 도착했을 때 `HEADER` 에 존재하는 토큰값이 유효한지 체크 후 결과를 `Response` 해주는 클래스 메서드.
* 이러한 클래스 메서드 방식을 이용하면 `Response`를 보낼 때 데이터와 메시지를 넣고 200 또는 400을 선택해서 보내는데 편리함.

`decode_jwt, make_jwt` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/functions.py#L40-L49)
* 계정을 인코딩하여 토큰을 만들거나 토큰을 디코딩하는 함수.

`check_username, check_username, check_passowrd` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/functions.py#L52-L81)  
* 계정 ID, PW, 전화번호 검사 함수 작성.

## 6. API 설계 및 작성

`AccountLoginView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L125-L139)   
* 입력 받은 username 이 있는지 DB 에서 조회 후 존재한다면 해당 username 에 대한 password 가 일치하는지 확인.
* 일치 시 해당 계정의 id 값을 이용하여 토큰을 만들고 토큰을 Response 에 담아서 return.
* `check_password()`를 이용하여 해당 유저의 비밀번호가 맞는지 확인 가능.

`AccountSignUpView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L142-L168)
* Body 를 통해 받은 username, password, phone 에 대한 조건이 충족되는지 확인.
* `User.objects.create_user()`를 이용하여 DB에 유저 생성.

`AccountChangePassword` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L171-L185)
* Body 를 통해 받은 현재 비밀번호가 유효한지 확인 후 유효하다면 입력 받은 새로운 비밀번호로 비밀번호를 변경함.
* `set_password()`를 통해 비밀번호 변경

`AccountDelete` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L188-L198)
* Body 를 통해 입력 받은 비밀번호를 통해 현재 비밀번호와 일치하는지 확인.
* 유효한 계정이 확인되면 `delete_user()`를 이용하여 DB 에서 계정 삭제.

`AccountUserProfile` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L201-L211)
* 유저의 정보를 모두 가져와서 Response 에 담아 보내줌.
* 유저의 구독 여부를 가져오는 메서드 사용 [is_subscription()](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/accounts/models.py#L44-L50)
* 유저의 구독 날짜를 가져오는 메서드 사용 [get_subscription_date()](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/accounts/models.py#L52-L55)
* 유저의 구독 날짜를 가져오는 메서드에서 `start_at__lte=now_time, end_at__gte=now_time`을 통해 날짜 필터링을 이용.

`AccountSubscribe` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L214-L221)
* 해당 유저의 구독 여부를 확인 후 구독이 되어있지 않다면 새로운 구독 정보를 생성하여 DB 에 저장.
* `SubscriptionLog.objects.create()`를 이용하여 새로운 구독 정보 생성.

`AccountUnsubscribe` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L224-L230)
* 해당 유저의 구독 여부를 확인 후 구독이 되어 있다면 구독을 취소.
* 유저의 구독을 해제하는 메서드 사용 [off_subscription()](https://github.com/KangJuSeong/sellerShop_server/blob/f053f8603cb8044d0b6d2954c2ec9c4326c3c0ea/shoppingmall_back/accounts/models.py#L57-L62)
* 구독 정보를 불러올때는 항상 이전 구독정보를 불러오지 않도록 오늘 날짜를 기준으로 필터링 해야 함.

`AccountWriteReview` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L233-L240)
* 리뷰 정보를 Body 를 통해 받은 후 해당 데이터를 DB 에 저장.
* `Review.objects.create()`를 이용.

`ReviewList` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L243-L251)
* 모든 리뷰 정보를 불러오기.
* Response 에 데이터를 담기 전 리뷰 작성 날짜 포맷팅 변경 후 보내주기.

`AccountByShopView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L21-L25)
* 현재 등록되어 있는 쇼핑몰별 계정의 개수를 response 해줌.
* `values('shop')` 구문을 이용하여 해당 계정에서 shop 필드의 값들만 가져오기.
* 동일한 shop 값을 가진 계정의 개수를 `annotate(count=Count('shop'))` 구문을 통해 계산한 후 쿼리셋에 추가해주기.

`DailyStatByAccountView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L28-L47)
* 파라미터로 shop 과 해당 shop 계정의 인덱스를 count 로 받기.
* 해당 shop 과 count(인덱스) 를 통해 유저의 쇼핑몰계정 정보 불러오기.
* count 가 필요한 이유는 같은 쇼핑몰 계정이 여러개일 수 있기 때문에 필요함.
* `importlib.import_module()` 구문을 통해 해당 shop 과 일치하는 크롤러 모듈을 불러오기.
* 해당 크롤러 모듈에 있는 `get_today_order_number()` 함수를 통해 전체 주문 개수와 배송 중인 주문의 개수를 response 해줌.

`AccountShopListView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L50-L61)
* 등록되어 있는 쇼핑몰 계정들을 모두 가져와서 response.

`AccountShopDeleteView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L64-L76)
* Body 를 통해 id 값을 받으면 해당 id 값을 가진 쇼핑몰 계정 정보 삭제.

`AccountShopCreateView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L79-L106)
* Body 를 통해 밭은 shop 값에 해당하는 쇼핑몰 크롤러를 불러오기.
* login_id, login_pw 값을 크롤러 모듈에 있는 `is_valid_account()` 함수를 이용하여 유효한 계정인지 확인.
* 해당 계정이 유효하다면 쇼핑몰 계정 DB 에 해당 계정이 존재하는지 확인.
* 유효한 계정이며 중복된 계정이 아닌게 확인되면 DB 에 쇼핑몰 계정 등록.

`NotceView` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L109-L122)
* DB 에 등록되어 있는 모든 공지 사항을 불러오고 Response 에 담아서 보내주기.

## 7. 쇼핑몰 별 크롤러 작성
* 쇼핑몰 별로 크롤러 모듈을 작성.
* `get_today_order_number()` 함수를 작성하여 금일 배송 중 및 주문 개수를 가져오기.
* `is_valid_account()` 함수를 작성하여 유효한 계정인지 확인.
* 크롤러 별로 session 값을 가져와서 리턴해주는 함수 작성.

### 1. coupang.py
`is_valid_account()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/coupang.py#L71-L74)
* `get_pdt()` 함수를 이용하여 리턴받은 값이 유효한 세션 값인지 확인 후 유효하다면 True 리턴.

`get_pdt()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/coupang.py#L65-L68)
* payload 에 _id, _pw 를 삽입.
* 해당 payload 와 로그인 url 을 `requests.post()` 메서드의 매개변수로 넣고 요청 후 돌아오는 응답의 쿠기 값에서 'pdt-boecn' 키의 값이 세션이므로 리턴.

`get_today_order_number()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/coupang.py#L6-L62)
* 금일 주문량과 배송 중인 수량을 가져오는 함수.
* 처음에 기존에 세션값이 없다면 `get_pdt()` 함수를 통해 세션값 가져와서 저장.
* 세션값을 헤더에 있는 쿠기값에 삽입, payload 에는 금일 날짜와 크롤링 해올 페이지를 입력 후 5번의 요청 실패가 일어나면 종료.
* `requests.get()` 메서드에 헤더와 payload 를 매개변수로 입력 후 응답 요청.
* 만약 세션값이 만료되었을 수 있으므로 요청 실패시 세션값을 한번 더 가져온 후 요청.
* 응답으로 온 lxml 형식의 데이터를 bs4 모듈을 이용하여 읽어오기.
* 가져온 값에서 배송 중인 주문의 갯수와 총 주문 개수를 저장하고 페이지가 더 존재한다면 다음 페이지로 가서 위 과정을 반복하고 최종적으로 shipped 와 total 값 리턴.

### 2. naver.py
`is_valid_account()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/naver.py#L87-L90)
* 'get_nsi()' 함수를 이용하여 리턴받은 값이 유효한 세션 값인지 확인 후 유효하다면 True 리턴.

`get_nsi()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/naver.py#L64-L84)
* payload 에 _id, _pw 를 넣고, 헤더 작성 후 `requests.post()` 메서드의 매개변수에 payload 와 헤더 삽입.
* 응답으로 온 리턴 값에서 쿠키값을 읽어 리턴.

`get_today_order()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/naver.py#L7-L52)
* 만약 세션값이 없다면 `get_nsi()` 함수를 이용하여 세션값을 가져오고 저장.
* payload 에 금일 날짜와 페이지를 넣고 헤더를 작성하여 `requests.get()` 메서드의 매개변수에 삽입 후 요청.
* 응답으로 온 데이터를 모으고 만약 해당 페이지의 총 주문 개수가 100개가 넘는다면 페이지를 증가시키고 100개가 안된다면 종료.
* 여기서 응답으로 온 데이터들은 모두 주문 정보.

`get_today_order_number()` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/d72ca6ff97aba40c2667bc6a61ff165e96a02b58/shoppingmall_back/crawler/naver.py#L55-L61)
* `get_today_order()` 함수를 통해 받은 주문 정보중 '배송중' 상태인 것은 shipped 를 1씩 증가시키고 전체 개수를 통해 total 값을 증가.
* shipped 와 total 값 리턴.

## 8. 개발 후
   








