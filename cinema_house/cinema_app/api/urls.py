from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from cinema_app.api.resourses import CustomUserCreateAPIView,  MovieSessionViewSet, PurchaseCreateAPIView, \
    ProfileApiView, LogoutApiView, CinemaHallViewSet

router = routers.SimpleRouter()
router.register(r'movie_session', MovieSessionViewSet)
router.register(r'cinema_hall', CinemaHallViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_auth_token),
    path('logout/', LogoutApiView.as_view()),
    path('registration/', CustomUserCreateAPIView.as_view()),
    path('cart/', PurchaseCreateAPIView.as_view()),
    path('profile/', ProfileApiView.as_view()),
    ]



