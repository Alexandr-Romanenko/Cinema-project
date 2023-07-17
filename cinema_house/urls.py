"""
This module defines the urlpatterns of the cinema_house.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from cinema_app.views import LoginUser, LogoutUser, RegistrationNewUser, CinemaHallCreateView, MovieSessionListView, \
    UpdateCinemaHallView, CinemaHallListView, MovieSessionCreateView, UpdateMovieSessionView, PurchaseCreateView, \
    MovieDetailsView, UserProfileView, MovieSessionTomorrowListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', LogoutUser.as_view(), name="logout"),
    path('registration/', RegistrationNewUser.as_view(), name="registration"),
    path('create_cinema_hall/', CinemaHallCreateView.as_view(), name='create_hall'),
    path('cinema_hall/', CinemaHallListView.as_view(), name='cinema_hall'),
    path('change_hall/<int:pk>/', UpdateCinemaHallView.as_view(), name='change_hall'),
    path('', MovieSessionListView.as_view(), name='cinema'),
    path('movie_session_tomorrow/', MovieSessionTomorrowListView.as_view(), name='movie_session_tomorrow'),
    path('create_movie_session/', MovieSessionCreateView.as_view(), name='create_movie_session'),
    path('change_movie_session/<int:pk>/', UpdateMovieSessionView.as_view(), name='change_movie_session'),
    path('cart/<int:pk>/', PurchaseCreateView.as_view(), name='cart'),
    path('movie_details/<int:pk>/', MovieDetailsView.as_view(), name='movie_details'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', include('cinema_app.urls'))
]
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



