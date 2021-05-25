## 쇼핑몰별 판매 현황 대쉬보드 (Intern)

### 1. 개발 목적
* 많은 쇼핑몰에서 같은 판매자들이 동일한 물품을 판매하고 있고, 판매 현황 관리를 위해서 각각의 쇼핑몰을 번거롭게 로그인하고 확인해야 함.
* 이러한 문제를 해결하기 위해 등록해놓은 쇼핑몰에 대한 판매 현황을 크롤링한 후 어플에서 한 눈에 확인 할 수 있도록 하여 효율적으로 판매 관리를 할 수 있음.

### 2. 개발 스택 및 도구
`Python`
`Django`
`Selenium`
`PostMan`
`Bitbucket`
`Jira`

### 3. 맡은 역할
* 쇼핑몰 별 판매 물품 현황 크롤링 모듈 만들기.
* 유저, 쇼핑몰 유저, 리뷰, 구독, 공지사항 모델링.
* 로그인, 회원가입, 리뷰, 구독, 공지사항 API 작성.
* 크롤링 한 데이터를 클라이언트로 보내주는 API 작성.

### 4. 모델 설계 및 작성
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

### 5. 필요한 모듈 개발

`APIView (utils/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/337a439a87aea4579bf588a2d885e23c84ea45d0/shoppingmall_back/utils/views.py#L10-L24)
* `APIView` 클래스는`JsonResponse`를 리턴해주는 클래스 메서드이며 HTTP 통신으로 `Request` 에 대한 `Response` 를 반환해주는 방식.   

`AuthAPIView (utils/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/views.py#L27-L41)   
* `AuthAPIView` 클래스는 `Request` 가 도착했을 때 `HEADER` 에 존재하는 토큰값이 유효한지 체크 후 결과를 `Response` 해주는 클래스 메서드.
* 이러한 클래스 메서드 방식을 이용하면 `Response`를 보낼 때 데이터와 메시지를 넣고 200 또는 400을 선택해서 보내는데 편리함.

`decode_jwt, make_jwt (utils/functions.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/functions.py#L40-L49)
* 계정을 인코딩하여 토큰을 만들거나 토큰을 디코딩하는 함수.

`check_username, check_username, check_passowrd (utils/functions.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/utils/functions.py#L52-L81)  
* 계정 ID, PW, 전화번호 검사 함수 작성.

### 6. API 설계 및 작성

`AccountLoginView (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L125-L139)   
* 입력 받은 username 이 있는지 DB 에서 조회 후 존재한다면 해당 username 에 대한 password 가 일치하는지 확인.
* 일치 시 해당 계정의 id 값을 이용하여 토큰을 만들고 토큰을 Response 에 담아서 return.
* `check_password()`를 이용하여 해당 유저의 비밀번호가 맞는지 확인 가능.

`AccountSignUpView (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L142-L168)
* Body 를 통해 받은 username, password, phone 에 대한 조건이 충족되는지 확인.
* `User.objects.create_user()`를 이용하여 DB에 유저 생성.

`AccountChangePassword (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L171-L185)
* Body 를 통해 받은 현재 비밀번호가 유효한지 확인 후 유효하다면 입력 받은 새로운 비밀번호로 비밀번호를 변경함.
* `set_password()`를 통해 비밀번호 변경

`AccountDelete (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L188-L198)
* Body 를 통해 입력 받은 비밀번호를 통해 현재 비밀번호와 일치하는지 확인.
* 유효한 계정이 확인되면 `delete_user()`를 이용하여 DB 에서 계정 삭제.

`AccountUserProfile (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L201-L211)
* 유저의 정보를 모두 가져와서 Response 에 담아 보내줌.
* 유저의 구독 여부를 가져오는 메서드 사용. [is_subscription()](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/accounts/models.py#L44-L50)
* 유저의 구독 날짜를 가져오는 메서드 사용. [get_subscription_date()](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/accounts/models.py#L52-L55)
* 유저의 구독 날짜를 가져오는 메서드에서 `start_at__lte=now_time, end_at__gte=now_time`을 통해 날짜 필터링을 이용.

`AccountSubscribe (apis/v1/views.py)` [Code](https://github.com/KangJuSeong/sellerShop_server/blob/0cc691ae359f7f96e16b0b3d9db29c3d49044ba3/shoppingmall_back/apis/v1/views.py#L214-L221)


### 7. 쇼핑몰 별 크롤러 작성

### 8. 개발 후
   








