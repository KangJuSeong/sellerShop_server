from django.urls import path

from apis.v1.views import (
    AccountByShopView, DailyStatByAccountView, AccountLoginView,
    AccountShopListView, AccountShopCreateView, AccountShopDeleteView,
    NoticeView, AccountSignUpView, AccountChangePassword, AccountDelete,
    AccountUserProfile, AccountSubscribe, AccountUnsubscribe, AccountWriteReview,
    ReviewList
)


urlpatterns = [
    path('stats/daily/by-account', DailyStatByAccountView.as_view(), name='v1_daily_stat_by_account'),
    path('accounts/by-shop', AccountByShopView.as_view(), name='v1_account_by_shop'),

    path('account/shop/list', AccountShopListView.as_view(), name='v1_account_shop_list'),
    path('account/shop/create', AccountShopCreateView.as_view(), name='v1_account_shop_create'),
    path('account/shop/delete', AccountShopDeleteView.as_view(), name='v1_account_shop_delete'),
    path('notice', NoticeView.as_view(), name='v1_notice'),

    path('account/login', AccountLoginView.as_view(), name='v1_account_login'),
    path('account/signup', AccountSignUpView.as_view(), name='v1_account_signup'),
    path('account/changePassword', AccountChangePassword.as_view(), name='v1_account_changePassword'),
    path('account/delete', AccountDelete.as_view(), name='v1_account_delete'),
    path('account/userProfile', AccountUserProfile.as_view(), name='v1_account_userProfile'),
    path('account/subscribe', AccountSubscribe.as_view(), name='v1_account_subscribe'),
    path('account/unsubscribe', AccountUnsubscribe.as_view(), name='v1_account_unsubscribe'),
    path('account/review', AccountWriteReview.as_view(), name='v1_account_review'),
    path('account/reviewList', ReviewList.as_view(), name='v1_account_reviewList'),
]