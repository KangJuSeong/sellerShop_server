from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

import random
from datetime import timedelta

from utils.models import CryptoModel


class ShopType(models.IntegerChoices):
    SMART_STORE = 0, '네이버 스마트스토어'
    COUPANG = 1, '쿠팡'
    ELEVENT_ST = 2, '11번가'
    AUCTION = 3, '옥션'
    GMARKET = 4, '지마켓(지9)'
    ESM = 5, '옥션, 지마켓(지9) 통합'

    @staticmethod
    def get_craw_module_by_shop():
        return {0: 'naver', 1: 'coupang', 2: 'elevenst', 3: 'esm', 4: 'esm', 5: 'esm'}


class ShopAccountInfo(CryptoModel):

    CRYPTO_FIELDS = ('login_id', 'login_pw', 'session',)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.SmallIntegerField(choices=ShopType.choices)
    login_id = models.CharField(max_length=255)
    login_pw = models.CharField(max_length=255)
    logo_uri = models.TextField(default='')
    session = models.TextField(default='')
    extra_data = models.TextField(default='')

    def __str__(self):
        return '%d. %s - %s(%s)' % (self.id, self.user.username, self.get_shop_display(), self._login_id)


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)

    def is_subscription(self):
        try:
            now_time = timezone.localtime()
            sub_obj = SubscriptionLog.objects.get(user=self, start_at__lte=now_time, end_at__gte=now_time, flag=True)
            return sub_obj
        except SubscriptionLog.DoesNotExist:
            return None

    def get_subscription_date(self):
        now_time = timezone.localtime()
        sub_obj = SubscriptionLog.objects.get(user=self, start_at__lte=now_time, end_at__gte=now_time, flag=True)
        return sub_obj.end_at + timedelta(hours=9)

    def off_subscription(self):
        now_time = timezone.localtime()
        sub_obj = SubscriptionLog.objects.get(user=self, start_at__lte=now_time, end_at__gte=now_time, flag=True)
        sub_obj.flag = False
        sub_obj.save()
        return sub_obj.flag

    def delete_user(self):
        random_name = str(random.random())
        self.username = 'delete_user' + random_name


class SubscriptionLog(models.Model):
    flag = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    write_at = models.DateTimeField()
    grade = models.SmallIntegerField()
    review = models.CharField(max_length=200)



