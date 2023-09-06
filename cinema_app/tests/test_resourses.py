from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from rest_framework import status
from datetime import date, timedelta
from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from freezegun import freeze_time
from rest_framework.authtoken.views import obtain_auth_token
from cinema_app.api.resourses import CustomUserCreateAPIView
from cinema_app.api.serializers import MovieSessionSerializer, PurchaseReadSerializer
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase


class GetTokenTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = CustomUser.objects.create_user(id=1, username='user', email='user@email.com', password='UserPass3')
        self.superuser = CustomUser.objects.create_superuser(id=2, username='admin', email='admin@email.com',
                                                             password='SuperPass2')

    def test_superuser_login(self):
        request = self.factory.post('/api/login/', {'username': 'admin', 'password': 'SuperPass2'})
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_superuser_login(self):
        request = self.factory.post('/api/login/', {'username': 'admin', 'password': 'Super2Pass'})
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_user_login(self):
        request = self.factory.post('/api/login/', {'username': 'user', 'password': 'UserPass3'})
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_user_login(self):
        request = self.factory.post('/api/login/', {'username': 'user1', 'password': 'UserPass3'})
        response = obtain_auth_token(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomUserCreateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_valid_user_registration(self):
        data = {'username': 'user', 'email': 'user@email.com', 'password': 'UserPass3'}
        request = self.factory.post('/api/registration/', data=data)
        response = CustomUserCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_user_registration(self):
        data = {'username': 'user1', 'email': 'user1@email.com', 'password': 'UP3'}
        request = self.factory.post('/api/registration/', data=data)
        response = CustomUserCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CinemaHallViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(id=1, username='user', email='user@email.com', password='UserPass3')
        self.superuser = CustomUser.objects.create_superuser(id=2, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        CinemaHall.objects.create(id=1, hall_name="Blue", hall_size=50)
        self.client = APIClient()

    def test_create_valid_hall_superuser(self):
        self.data = {'hall_name': 'White', 'hall_size': 100}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post('/api/cinema_hall/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'hall_name': 'White', 'hall_size': 100, 'id': 2})

    def test_create_invalid_hall_superuser(self):
        self.data = {'hall_name': 'Green', 'hall_size': 0}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post('/api/cinema_hall/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_hall_user(self):
        self.data = {'hall_name': 'Black', 'hall_size': 100}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cinema_hall/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_valid_hall_superuser(self):
        self.data = {'hall_name': 'Red', 'hall_size': 200}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.put('/api/cinema_hall/1/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'hall_name': 'Red', 'hall_size': 200, 'id': 1})

    def test_get_hall_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/cinema_hall/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_hall_list_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cinema_hall/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_hall_list_anonymous_user(self):
        response = self.client.get('/api/cinema_hall/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MovieSessionViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=2, username='user', email='user@email.com', password='UserPass3')

        CinemaHall.objects.create(id=1, hall_name='Black', hall_size=30)
        hall = CinemaHall.objects.get(id=1)

        MovieSession.objects.create(id=1,
                                    hall=hall,
                                    movie_title="Test movie session #1",
                                    movie_description="All about creation tests movie #1",
                                    session_start_time="21:00",
                                    session_end_time="22:00",
                                    session_show_start_date=(datetime.now().date() - timedelta(days=2)),
                                    session_show_end_date=(datetime.now().date() + timedelta(days=5)),
                                    free_seats=hall.hall_size,
                                    ticket_price=2500)

        MovieSession.objects.create(id=2,
                                    hall=hall,
                                    movie_title="Test movie session #2",
                                    movie_description="All about creation tests movie #2",
                                    session_start_time="22:10",
                                    session_end_time="23:00",
                                    session_show_start_date=(datetime.now().date() - timedelta(days=1)),
                                    session_show_end_date=(datetime.now().date() + timedelta(days=7)),
                                    free_seats=hall.hall_size,
                                    ticket_price=1500)

    def test_create_valid_movie_session_superuser(self):
        self.data = {'hall': 1,
                     'movie_title': 'CreateTestMovie',
                     'movie_description': 'All about creation tests movie',
                     'session_start_time': '11:00:00',
                     'session_end_time': '12:00:00',
                     'session_show_start_date': (datetime.now().date() + timedelta(days=1)),
                     'session_show_end_date': (datetime.now().date() + timedelta(days=15)),
                     'ticket_price': 2000}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post('/api/movie_session/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'id': 3,
                                         'hall': 1,
                                         'movie_title': 'CreateTestMovie',
                                         'movie_description': 'All about creation tests movie',
                                         'session_start_time': '11:00:00',
                                         'session_end_time': '12:00:00',
                                         'session_show_start_date': str((datetime.now().date() + timedelta(days=1))),
                                         'session_show_end_date': str((datetime.now().date() + timedelta(days=15))),
                                         'free_seats': 30,
                                         'ticket_price': 2000})

    def test_create_invalid_movie_session_superuser(self):
        self.data = {'hall': 1,
                     'movie_title': '',
                     'movie_description': 'All about creation tests movie',
                     'session_start_time': '11:00',
                     'session_end_time': '12:00',
                     'session_show_start_date': '2023-08-01',
                     'session_show_end_date': '2023-08-08',
                     'free_seats': 50,
                     'ticket_price': 2000}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post('/api/movie_session/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_movie_session_user(self):
        self.data = {'hall': 1,
                     'movie_title': 'The best movie',
                     'movie_description': 'All about the best movie',
                     'session_start_time': '13:00',
                     'session_end_time': '14:00',
                     'session_show_start_date': (datetime.now().date()),
                     'session_show_end_date': (datetime.now().date() + timedelta(days=15)),
                     'ticket_price': 10000}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/movie_session/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid_update_movie_session_superuser(self):
        self.data = {"hall": 1,
                     "movie_title": "Test update valid cinema session superuser",
                     "movie_description": "All about creation tests movie",
                     "session_start_time": "23:30",
                     "session_end_time": "23:55",
                     "session_show_start_date": (datetime.now().date()),
                     "session_show_end_date": (datetime.now().date() + timedelta(days=5)),
                     "ticket_price": 2500}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.put('/api/movie_session/2/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_movie_session_superuser(self):
        self.data = {
            "hall": 1,
            "movie_title": "T",
            "movie_description": "All about creation tests movie",
            "session_start_time": "22:30",
            "session_end_time": "23:00",
            "session_show_start_date": (datetime.now().date()),
            "session_show_end_date": (datetime.now().date() + timedelta(days=5)),
            "ticket_price": 2500}
        self.client.force_authenticate(user=self.superuser)
        response = self.client.put('/api/movie_session/2/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_movie_session_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/movie_session/')
        self.assertEqual(response.status_code, 200)

    def test_get_movie_session_list_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/movie_session/')
        self.assertEqual(response.status_code, 200)

    def test_get_movie_session_list_anonymous_user(self):
        self.client.force_authenticate(user=AnonymousUser())
        response = self.client.get('/api/movie_session/')
        self.assertEqual(response.status_code, 200)

    def test_get_movie_session_list_sort_today_action(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/movie_session/', session_show_day='today')
        queryset = MovieSession.objects.filter(session_show_start_date__lte=date.today(),
                                               session_show_end_date__gt=date.today())
        serializer = MovieSessionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_movie_session_list_sort_tomorrow_action(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/movie_session/', session_show_day='tomorrow')
        queryset = MovieSession.objects.filter(session_show_start_date__lte=date.today() + timedelta(days=1),
                                               session_show_end_date__gt=date.today())
        serializer = MovieSessionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_movie_session_list_sort_hall_action(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/movie_session/', hall=1)
        queryset = MovieSession.objects.filter(hall_id=1)
        serializer = MovieSessionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)


@freeze_time('2023-08-01')
class PurchaseCreateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(id=1, username='customer', email='user@email.com',
                                                   password='UserPass3')

        CinemaHall.objects.create(id=1, hall_name='Best', hall_size=5)
        hall = CinemaHall.objects.get(id=1)

        MovieSession.objects.create(id=1,
                                    hall=hall,
                                    movie_title="Test best movie session",
                                    movie_description="All about tests movie session",
                                    session_start_time="15:00:00",
                                    session_end_time="17:00:00",
                                    session_show_start_date="2023-08-01",
                                    session_show_end_date="2023-08-30",
                                    free_seats=hall.hall_size,
                                    ticket_price=2500)

    def test_create_purchase_object_user(self):
        self.data = {'movie': 1, 'quantity': 2}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'id': 1, 'user': 1, 'movie': 1, 'purchase_date': '2023-08-01',
                                         'purchase_sum': 5000, 'quantity': 2})

    def test_create_purchase_object_anonymous_user(self):
        self.data = {'movie': 1, 'quantity': 2}
        self.client.force_authenticate(user=AnonymousUser())
        response = self.client.post('/api/cart/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_purchase_object_user_with_invalid_quantity(self):
        self.data = {'movie': 1, 'quantity': 500}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time('2023-08-01 16:05:00')
    def test_create_purchase_object_user_with_invalid_time(self):
        self.data = {'movie': 1, 'quantity': 2}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_purchase_object_user_without_movie_object(self):
        self.data = {'movie': 10, 'quantity': 2}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileApiViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperAdmin2')
        self.user = CustomUser.objects.create_user(id=2, username='buyer', email='buyer@email.com',
                                                   password='UserPass3')
        self.user_stranger = CustomUser.objects.create_user(id=3, username='stranger', email='stranger@email.com',
                                                            password='SuperPas18')

        self.hall = CinemaHall.objects.create(id=1, hall_name='New', hall_size=10)

        self.movie = MovieSession.objects.create(id=1,
                                                 hall=self.hall,
                                                 movie_title="Test profile api view",
                                                 movie_description="All about tests movie session",
                                                 session_start_time="15:00:00",
                                                 session_end_time="17:00:00",
                                                 session_show_start_date="2023-08-01",
                                                 session_show_end_date="2023-08-30",
                                                 free_seats=self.hall.hall_size,
                                                 ticket_price=2500)

        Purchase.objects.create(id=1, user=self.user, movie=self.movie, purchase_date='2023-08-01',
                                purchase_sum=5000, quantity=2)
        Purchase.objects.create(id=2, user=self.user, movie=self.movie, purchase_date='2023-08-01',
                                purchase_sum=10000, quantity=4)
        Purchase.objects.create(id=3, user=self.user_stranger, movie=self.movie, purchase_date='2023-08-01',
                                purchase_sum=7500, quantity=3)

    def test_get_purchase_list_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/')
        queryset = Purchase.objects.filter(user=self.user)
        serializer = PurchaseReadSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_purchase_list_user_stranger(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/')
        queryset = Purchase.objects.filter(user=self.user_stranger)
        serializer = PurchaseReadSerializer(queryset, many=True)
        self.assertNotEqual(response.data['results'], serializer.data)

    def test_get_purchase_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/profile/')
        queryset = Purchase.objects.all()
        serializer = PurchaseReadSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)
