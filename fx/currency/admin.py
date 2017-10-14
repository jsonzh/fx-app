from django.contrib import admin

from .models import Currency,Bank,Rate

admin.site.register(Currency)
admin.site.register(Bank)
admin.site.register(Rate)