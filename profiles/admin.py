from django.contrib import admin
from .models import Profile, ResetPassword


class AD(admin.ModelAdmin):
    list_display = 'user', 'ip', 'first_ip'

    class Meta:
        model = Profile


admin.site.register(Profile, AD)
admin.site.register(ResetPassword)
