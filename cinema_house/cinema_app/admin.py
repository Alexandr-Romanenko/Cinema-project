from django.contrib import admin
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase

# Register your models here.


admin.site.register(CustomUser)
admin.site.register(CinemaHall)
admin.site.register(MovieSession)
admin.site.register(Purchase)
