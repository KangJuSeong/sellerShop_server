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
* `APIView` 클래스는`JsonResponse`를 리턴해주는 클래스 메서드이며 HTTP 통신으로 `Request` 에 대한 `Response` 를 반환해주는 방식.
    ```python
    class APIView(View):
    @classmethod
    def raw_response(cls, content: dict, status: int = 200) -> JsonResponse:
        return JsonResponse(content, status=status)
    
    def response(self, data, message, status):
        return self.raw_response({'data': data, 'message': message, 'status': status}, status)
    
    # 200 응답을 리턴해주는 함수
    def success(self, data=None, message='') -> JsonResponse:
        return self.response(data, message, 200)
    
    # 400 응답을 리턴해주는 함수
    def fail(self, data=None, message='', status: int = 400) -> JsonResponse:
        return self.response(data, message, status)
    ```
* `AuthAPIView` 클래스는 `Request` 가 도착했을 때 `HEADER` 에 존재하는 토큰값이 유효한지 체크 후 결과를 `Response` 해주는 클래스 메서드.
* 이러한 클래스 메서드 방식을 이용하면 `Response`를 보낼 때 데이터와 메시지를 넣고 200 또는 400을 선택해서 보내는데 편리함.
    ```python
    class AuthAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        # 헤더에 담긴 토큰 값 읽어오기
        token = request.META.get('HTTP_AUTHORIZATION', '')
        # 토큰값 앞에 있는 배리어 체크
        if len(token) > 7:
            data = decode_jwt(token[7:])
            try:
                request.user = User.objects.get(id=data['id'])
            except (User.DoesNotExist, TypeError):
                return self.fail('Invalid Auth')
        else:
            return self.fail('Invalid Auth')
    
        return super(AuthAPIView, self).dispatch(request, *args, **kwargs)  
    ```
  
* 계정을 인코딩하여 토큰을 만들거나 토큰을 디코딩하는 함수.
    ```python
    utils/function.py
    import jwt
    from django.contrib.auth.models import User
    from jwt import InvalidSignatureError
    
    # JWT_KEY 는 환경 변수
    def make_jwt(user: User):
        return jwt.encode({'id': user.id}, JWT_KEY, algorithm='HS256')
    
    def decode_jwt(token: str):
        try:
            return jwt.decode(token.encode(), JWT_KEY, algorithms='HS256')
        except InvalidSignatureError:
            pass
        return ''
    ```

* 계정 ID, PW, 전화번호 검사 함수 작성.
```python
utils/function.py
import re
import string

# 아이디 조건 체크
def check_username(username):
    size = len(username)
    if size < 5:
        return 0, "Short id"
    elif size > 20:
        return 0, "Long id"
    if any(check in username for check in string.ascii_uppercase):
        return 0, "Uppercase id"
    if any(check in username for check in ' !@#$%^&*()-_+=`~;:/?.>,<\\|[]{}'):
        return 0, "special characters id"
    return 1, "success"

# 비밀전호 조건 체크
def check_password(password):
    size = len(password)
    if size < 8:
        return 0, "Short pw"
    elif size > 16:
        return 0, "Long pw"
    else:
        return 1, "success"

# 전화번호 양식 체크, 정규 표현식 사용
def check_phone(phone):
    regex = re.compile(r'^\d{3}-?(\d{4}|\d{3})-?\d{4}$')
    check = regex.search(phone)
    if check:
        return 1, "success"
    else:
        return 0, "Invalid number"
```

### 6. API 설계 및 작성

* 로그인 API
```python
class AccountLoginView(APIView):
    
    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        try:
            user = User.objects.get(username=data['username'])
            if not user.check_password(data['password']):
                return self.fail(message="incorrect password")
            else:
                login(self.request, user)
                token = make_jwt(user).decode()
                return self.success(data=token, message='success')
        except User.DoesNotExist:
            return self.fail(message="not exist")
```
```python
class AccountSignUpView(APIView):
    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        try:
            if data['username'] == '':
                return self.fail(message="Empty id")
            elif data['password'] == '':
                return self.fail(message="Empty password")
            elif data['phone'] == '':
                return self.fail(message="Empty phone")
            id_flag, id_message = check_username(data['username'])
            if not id_flag:
                return self.fail(message=id_message)
            pw_flag, pw_message = check_password(data['password'])
            if not pw_flag:
                return self.fail(message=pw_message)
            hp_flag, hp_message = check_phone(data['phone'])
            if not hp_flag:
                return self.fail(message=hp_message)
            User.objects.create_user(username=data['username'], password=data['password'], phone=data['phone'])
            user = User.objects.get(username=data['username'])
            login(self.request, user)
            token = make_jwt(user).decode()
            return self.success(data=token, message="success")
        except IntegrityError:
            return self.fail(message="Duplicate account")


class AccountChangePassword(AuthAPIView):
    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        user = self.request.user
        if not user.check_password(data['current_password']):
            return self.fail(message="incorrect password")
        else:
            pw_flag, message = check_password(data['new_password'])
            if pw_flag:
                user.set_password(data['new_password'])
                user.save()
                return self.success(message=message)
            else:
                return self.fail(message=message)


class AccountDelete(AuthAPIView):
    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        user = self.request.user
        if not user.check_password(data['password']):
            return self.fail(message="incorrect password")
        else:
            user.delete_user()
            user.save()
            return self.success(message="success")


class AccountUserProfile(AuthAPIView):
    def get(self, *args, **kwargs):
        if self.request.user.is_subscription():
            date = self.request.user.get_subscription_date().strftime("%Y/%m/%d %H:%M")
            data = {'username': self.request.user.username, 'phone': self.request.user.phone,
                    'subscribe': date}
            return self.success(data=data)
        else:
            data = {'username': self.request.user.username, 'phone': self.request.user.phone,
                    'subscribe': "구독하지 않으셨습니다."}
            return self.fail(data=data)
```








