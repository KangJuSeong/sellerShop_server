import importlib
import json
from datetime import timedelta

from django.db.utils import IntegrityError
from django.db.models import Count
from django.contrib.auth import login, get_user_model
from django.utils import timezone

from utils.views import AuthAPIView, APIView
from utils.functions import make_jwt, check_password, check_phone, check_username

from accounts.models import ShopAccountInfo, ShopType, SubscriptionLog, Review
from notices.models import Notice


CRAWL_MODULE_BY_SHOP = ShopType.get_craw_module_by_shop()
User = get_user_model()


class AccountByShopView(AuthAPIView):

    def get(self, *args, **kwargs):
        query_set = ShopAccountInfo.objects.filter(user=self.request.user).values('shop').annotate(count=Count('shop'))
        return self.success([s for s in query_set])


class DailyStatByAccountView(AuthAPIView):

    def get(self, *args, **kwargs):

        try:
            shop_idx = int(self.request.GET.get('shop', 0))
            count = int(self.request.GET.get('count', 0))

            obj = ShopAccountInfo.objects.filter(user=self.request.user).filter(shop=shop_idx)[count]
            module = importlib.import_module('crawler.%s' % CRAWL_MODULE_BY_SHOP[obj.shop])

            numbers = module.get_today_order_number(obj)
            return self.success({
                'shipped': numbers['shipped'], 'total': numbers['total'], 'key': '%s-%s' % (shop_idx, count),
                'shop_logo_uri': obj.logo_uri, 'account': obj._login_id, 'shop': obj.get_shop_display().split()[-1],
            })

        except (IndexError, ValueError):
            pass
        return self.fail()


class AccountShopListView(AuthAPIView):

    def get(self, *args, **kwargs):
        data = {'shops': []}

        for info in ShopAccountInfo.objects.filter(user=self.request.user):
            shop_name = info.get_shop_display().split()[-1]
            data['shops'].append({
                'account': info._login_id, 'shop': shop_name,
                'shop_logo_uri': info.logo_uri, 'id': info.id,
            })
        return self.success(data)


class AccountShopDeleteView(AuthAPIView):

    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)

        try:
            target = ShopAccountInfo.objects.get(id=data['id'])
            target.delete()
        except ShopAccountInfo.DoesNotExist:
            return self.fail(data={'code': 0}, message="the target object does not exist.")

        return self.success(message="success")


class AccountShopCreateView(AuthAPIView):

    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        if data.get('shop', -1) < 0:
            return self.fail(data={'code': 0}, message='invalid request')

        module = importlib.import_module('crawler.%s' % CRAWL_MODULE_BY_SHOP[data['shop']])
        if not module.is_valid_account(data.get('login_id', ''), data.get('login_pw', '')):
            return self.fail(data={'code': 1}, message='invalid data')

        is_exist = ShopAccountInfo.objects.filter(
            login_id=data['login_id'], login_pw=data['login_pw'], shop=data['shop']
        ).exists()
        if is_exist:
            return self.fail(data={'code': 2}, message="is already exist id.")

        info = ShopAccountInfo.objects.create(
            user=self.request.user, login_id=data['login_id'], login_pw=data['login_pw'], shop=data['shop']
        )
        if 3 <= info.shop <= 5:
            info.extra_data = importlib.import_module(
                'crawler.%s' % CRAWL_MODULE_BY_SHOP[info.shop]
            ).get_esm_account_id(info)
            info.save()

        return self.success(message="success")


class NoticeView(APIView):

    def get(self, *args, **kwargs):
        notice_set = []

        notices = Notice.objects.all()

        for notice in notices:
            notice_set.append({
                "title": notice.title,
                "content": notice.content,
            })

        return self.success(data={'notices': notice_set}, message="success")


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


class AccountSubscribe(AuthAPIView):
    def get(self, *args, **kwargs):
        if not self.request.user.is_subscription():
            SubscriptionLog.objects.create(user=self.request.user, start_at=timezone.localtime(),
                                           end_at=timezone.localtime() + timedelta(days=30), flag=1)
            return self.success(message="success")
        else:
            return self.fail(message="already subscribe")


class AccountUnsubscribe(AuthAPIView):
    def get(self, *args, **kwargs):
        if self.request.user.is_subscription():
            self.request.user.off_subscription()
            return self.success(message="success unsubscribe")
        else:
            return self.fail(message="already unsubscribe")


class AccountWriteReview(AuthAPIView):
    def post(self, *args, **kwargs):
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        grade = int(data['grade'])
        Review.objects.create(user=self.request.user, write_at=timezone.localtime(),
                              grade=grade, review=data['review'])
        return self.success(message='success')


class ReviewList(AuthAPIView):
    def get(self, *args, **kwargs):
        review_list = Review.objects.all()
        data = {}
        for review in review_list:
            date = (review.write_at + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M")
            data[review.id] = {'review': review.review, 'grade': review.grade,
                               'write_at': date, 'user': review.user.username}
        return self.success(data=data, message='success')
