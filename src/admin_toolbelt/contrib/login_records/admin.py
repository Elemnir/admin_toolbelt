from django.contrib import admin

from .models import LoginRecord, LoginRecordToken


class LoginRecordAdmin(admin.ModelAdmin):
    pass
admin.site.register(LoginRecord, LoginRecordAdmin)


class LoginRecordTokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(LoginRecordToken, LoginRecordTokenAdmin)

