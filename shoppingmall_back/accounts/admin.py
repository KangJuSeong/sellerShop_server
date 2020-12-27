from django.contrib import admin


from accounts.models import ShopAccountInfo
from accounts.models import User


@admin.register(ShopAccountInfo)
class ShopAccountInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
