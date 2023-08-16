from datetime import time, date
from unittest.mock import patch
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from freezegun import freeze_time
from cinema_app.forms import UserCreateForm
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from cinema_app.views import LoginUser, CinemaHallCreateView, MovieSessionListView, \
    UpdateCinemaHallView, CinemaHallListView, MovieSessionCreateView, UpdateMovieSessionView, PurchaseCreateView, \
    MovieDetailsView, UserProfileView


class RegistrationNewUserTest(TestCase):
    def setUp(self):
        self.form_data = {
            'username': 'test_user',
            'email': 'test_user@email.com',
            'password1': 'SuperPass3',
            'password2': 'SuperPass3'}

        self.c = Client()

    def test_register_redirect(self):
        form = UserCreateForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/registration/', form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')

    def test_register_user_created(self):
        form = UserCreateForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/registration/', form.cleaned_data)
        self.assertTrue(CustomUser.objects.filter(username='test_user').exists())


class LoginViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CustomUser.objects.create(username='test1', email='user1@email.com', password='SuperPass3')
        self.data = {'username': 'test1', 'password': 'SuperPass3'}

    def test_availability(self):
        factory = RequestFactory()
        request = factory.get('/login')
        request.user = AnonymousUser()
        response = LoginUser.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_logged(self):
        response = self.c.post('/login/', self.data)
        self.assertEqual(response.status_code, 200)


class CinemaHallCreateViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=1, username='user1', email='user1@email.com',
                                                   password='Superuser1')

        self.request = self.factory.post('/cinema_hall/', {'hall_name': 'White', 'hall_size': 100})

    def test_create_cinema_hall_superuser(self):
        request = self.request
        request.user = self.superuser
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cinema_hall/')

    @patch('cinema_app.views.messages.error')
    def test_create_cinema_hall_anonymous_user(self, error):
        request = self.request
        request.user = AnonymousUser()
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @patch('cinema_app.views.messages.error')
    def test_create_cinema_hall_user(self, error):
        request = self.request
        request.user = self.user
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')


class CinemaHallListViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=1, username='user', email='user@email.com',
                                                   password='Superuser1')

        self.request = self.factory.post('/cinema_hall/', {'hall_name': 'Purl', 'hall_size': 10})

    def test_list_hall_user(self):
        request = self.factory.get('/cinema_hall/')
        request.user = self.user
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_list_hall_superuser(self):
        request = self.factory.get('/cinema_hall/')
        request.user = self.superuser
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    @patch('cinema_app.views.messages.error')
    def test_list_hall_anonymous_user(self, error):
        request = self.factory.get('/cinema_hall/')
        request.user = AnonymousUser()
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')


class UpdateCinemaHallViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        CinemaHall.objects.create(id=1, hall_name='White', hall_size=300)

        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=1, username='user1', email='user1@email.com',
                                                   password='Superuser1')

        self.request = self.factory.post('/change_hall/1/', {'id': 1, 'hall_name': 'Gold', 'hall_size': 100})

    def test_update_cinema_hall_superuser(self):
        request = self.request
        request.user = self.superuser
        response = UpdateCinemaHallView.as_view()(request, pk=1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cinema_hall/')

    @patch('cinema_app.views.messages.error')
    def test_update_cinema_hall_anonymous_user(self, error):
        request = self.request
        request.user = AnonymousUser()
        response = UpdateCinemaHallView.as_view()(request, pk=1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @patch('cinema_app.views.messages.error')
    def test_update_cinema_hall_user(self, error):
        request = self.request
        request.user = self.user
        response = UpdateCinemaHallView.as_view()(request, pk=1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')


class MovieSessionListViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=2, username='user1', email='user1@email.com',
                                                   password='Superuser1')

        CinemaHall.objects.create(id=3, hall_name="Blue", hall_size=100)
        hall = CinemaHall.objects.get(id=3)

        MovieSession.objects.create(
            id=2,
            hall=hall,
            movie_title='TestMovie',
            movie_description='All about test movie',
            session_start_time='07:45',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2000)

        MovieSession.objects.create(
            id=3,
            hall=hall,
            movie_title='NewSuperMovie',
            movie_description='All about new movie',
            session_start_time='10:45',
            session_end_time='12:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2000)

        self.request = self.factory.get('/')

    def test_movie_list_superuser(self):
        request = self.request
        request.user = self.superuser
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_user(self):
        request = self.request
        request.user = self.user
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_anonymous_user(self):
        request = self.request
        request.user = AnonymousUser
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    @freeze_time('2023-08-01')
    def test_get_queryset_method(self):
        request = self.request
        request.user = self.user
        response = MovieSessionListView.as_view()(request)
        view = MovieSessionListView()
        view.request = request
        qs = view.get_queryset()
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(qs, MovieSession.objects.filter(session_show_end_date__gt=timezone.now()))


class MovieSessionCreateViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass2')
        self.user = CustomUser.objects.create_user(id=3, username='user1', email='user1@email.com',
                                                   password='Superuser1')

        CinemaHall.objects.create(id=5, hall_name="Blue", hall_size=100)

        self.request = self.factory.post('/create_movie_session/',
                                         {'id': 7,
                                          'hall': 5,
                                          'movie_title': 'CreateTestMovie',
                                          'movie_description': 'All about creation tests movie',
                                          'session_start_time': '07:45',
                                          'session_end_time': '10:00',
                                          'session_show_start_date': '2023-08-01',
                                          'session_show_end_date': '2023-08-08',
                                          'free_seats': 100,
                                          'ticket_price': 2000})

    @patch('cinema_app.views.messages.error')
    def test_create_movie_session_user(self, error):
        request = self.request
        request.user = self.user
        response = MovieSessionCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @patch('cinema_app.views.messages.error')
    def test_create_movie_session_anonymous_user(self, error):
        request = self.request
        request.user = AnonymousUser()
        response = MovieSessionCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @freeze_time('2023-08-01')
    def test_create_movie_session_superuser(self):
        request = self.factory.post('/create_movie_session/',
                                    {'id': 1,
                                     'hall': 5,
                                     'movie_title': 'CreateTestMovie',
                                     'movie_description': 'All about creation tests movie',
                                     'session_start_time': '07:45',
                                     'session_end_time': '10:00',
                                     'session_show_start_date': '2023-08-01',
                                     'session_show_end_date': '2023-08-08',
                                     'free_seats': 100,
                                     'ticket_price': 2000})
        request.user = self.superuser
        response = MovieSessionCreateView.as_view()(request, pk=5)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        movie_obj = MovieSession.objects.get(id=1)
        hall = CinemaHall.objects.get(id=5)
        self.assertEqual(movie_obj.hall, hall)
        self.assertEqual(movie_obj.movie_title, 'CreateTestMovie')
        self.assertEqual(movie_obj.movie_description, 'All about creation tests movie')
        self.assertEqual(movie_obj.session_start_time, time.fromisoformat('07:45'))
        self.assertEqual(movie_obj.session_end_time, time.fromisoformat('10:00'))
        self.assertEqual(movie_obj.session_show_start_date, date.fromisoformat('2023-08-01'))
        self.assertEqual(movie_obj.session_show_end_date, date.fromisoformat('2023-08-08'))
        self.assertEqual(movie_obj.free_seats, 100)
        self.assertEqual(movie_obj.ticket_price, 2000)


@freeze_time('2023-08-01')
class UpdateMovieSessionViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=1, username='admin', email='admin@email.com',
                                                             password='SuperPass')
        self.user = CustomUser.objects.create_user(id=2, username='user', email='user@email.com',
                                                   password='Superuser')
        CinemaHall.objects.create(id=3, hall_name="Gold", hall_size=10)
        hall = CinemaHall.objects.get(id=3)

        MovieSession.objects.create(id=4,
                                    hall=hall,
                                    movie_title='CreateTestMovie',
                                    movie_description='All about creation tests movie',
                                    session_start_time='10:45',
                                    session_end_time='12:00',
                                    session_show_start_date='2023-08-01',
                                    session_show_end_date='2023-08-08',
                                    free_seats=hall.hall_size,
                                    ticket_price=1000)

    @freeze_time('2023-08-01')
    def test_update_movie_session_superuser(self):
        request = self.factory.post('change_movie_session/4/',
                                    {'id': 4,
                                     'hall': 3,
                                     'movie_title': 'TestMovieSession',
                                     'movie_description': 'All about creation tests movie',
                                     'session_start_time': '07:00',
                                     'session_end_time': '09:00',
                                     'session_show_start_date': '2023-08-01',
                                     'session_show_end_date': '2023-08-08',
                                     'free_seats': 10,
                                     'ticket_price': 1000})
        request.user = self.superuser
        response = UpdateMovieSessionView.as_view()(request, pk=4)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        movie_obj = MovieSession.objects.get(id=4)
        hall = CinemaHall.objects.get(id=3)
        self.assertEqual(movie_obj.hall, hall)
        self.assertEqual(movie_obj.movie_title, 'TestMovieSession')
        self.assertEqual(movie_obj.movie_description, 'All about creation tests movie')
        self.assertEqual(movie_obj.session_start_time, time.fromisoformat('07:00'))
        self.assertEqual(movie_obj.session_end_time, time.fromisoformat('09:00'))
        self.assertEqual(movie_obj.session_show_start_date, date.fromisoformat('2023-08-01'))
        self.assertEqual(movie_obj.session_show_end_date, date.fromisoformat('2023-08-08'))
        self.assertEqual(movie_obj.free_seats, 10)
        self.assertEqual(movie_obj.ticket_price, 1000)

    @freeze_time('2023-08-01')
    @patch('cinema_app.views.messages.error')
    def test_update_movie_session_user(self, error):
        request = self.factory.post('change_movie_session/4/',
                                    {'id': 4,
                                     'hall': 3,
                                     'movie_title': 'TestMovieSessionUpdateUser',
                                     'movie_description': 'All about creation tests movie',
                                     'session_start_time': '08:00',
                                     'session_end_time': '10:00',
                                     'session_show_start_date': '2023-08-01',
                                     'session_show_end_date': '2023-08-08',
                                     'free_seats': 10,
                                     'ticket_price': 3000})
        request.user = self.user
        response = UpdateMovieSessionView.as_view()(request, pk=4)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @freeze_time('2023-08-01')
    @patch('cinema_app.views.messages.error')
    def test_update_movie_session_anonymous_user(self, error):
        request = self.factory.post('change_movie_session/4/',
                                    {'id': 4,
                                     'hall': 3,
                                     'movie_title': 'TestMovieSessionUpdateAnonymousUser',
                                     'movie_description': 'All about creation tests movie',
                                     'session_start_time': '07:00',
                                     'session_end_time': '09:00',
                                     'session_show_start_date': '2023-08-01',
                                     'session_show_end_date': '2023-08-08',
                                     'free_seats': 10,
                                     'ticket_price': 2000})
        request.user = self.user
        response = UpdateMovieSessionView.as_view()(request, pk=4)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')


class MovieSessionTomorrowListViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(id=5, username='admin', email='adm@email.com',
                                                             password='SuperAdmPas')
        self.user = CustomUser.objects.create_user(id=6, username='user18', email='user18@email.com',
                                                   password='Superuser18')

        CinemaHall.objects.create(id=7, hall_name="Black", hall_size=111)
        hall = CinemaHall.objects.get(id=7)

        MovieSession.objects.create(
            id=8,
            hall=hall,
            movie_title='TestMovieTomorrow',
            movie_description='All about test movie tomorrow',
            session_start_time='08:00',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=1500)

        MovieSession.objects.create(
            id=9,
            hall=hall,
            movie_title='NewSuperMovieTomorrow',
            movie_description='All about new movie tomorrow',
            session_start_time='10:15',
            session_end_time='12:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2500)

        self.request = self.factory.get('/')

    def test_movie_list_superuser(self):
        request = self.request
        request.user = self.superuser
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_user(self):
        request = self.request
        request.user = self.user
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_anonymous_user(self):
        request = self.request
        request.user = AnonymousUser
        response = MovieSessionListView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class PurchaseCreateViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(id=8, username='buyer', email='buyer@email.com',
                                                   password='SuperUser18')
        CinemaHall.objects.create(id=9, hall_name="Orange", hall_size=10)
        hall = CinemaHall.objects.get(id=9)
        MovieSession.objects.create(
            id=10,
            hall=hall,
            movie_title='NewBestSuperMovie',
            movie_description='All about new best movie',
            session_start_time='10:15',
            session_end_time='12:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2500)
        self.request = self.factory.post('cart/10/', {'quantity': 2})

    @patch('cinema_app.views.messages.error')
    def test_purchased_anonymous_user(self, error):
        request = self.request
        request.user = AnonymousUser()
        response = PurchaseCreateView.as_view()(request, pk=10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    @freeze_time('2023-08-01')
    def test_purchased_user(self):
        request = self.request
        request.user = self.user
        response = PurchaseCreateView.as_view()(request, pk=10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_purchased_user_with_invalid_zero_quantity(self, error):
        request = self.factory.post('cart/10/', {'quantity': 0})
        request.user = self.user
        response = PurchaseCreateView.as_view()(request, pk=10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_purchased_user_with_invalid_enormous_quantity(self, error):
        request = self.factory.post('cart/10/', {'quantity': 1000})
        request.user = self.user
        response = PurchaseCreateView.as_view()(request, pk=10)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class MovieDetailsViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(id=1, username='user', email='user@email.com',
                                                   password='Superuser8')

        CinemaHall.objects.create(id=2, hall_name="Grey", hall_size=100)
        hall = CinemaHall.objects.get(id=2)

        MovieSession.objects.create(
            id=3,
            hall=hall,
            movie_title='TestMovie2',
            movie_description='All about test movie 2',
            session_start_time='08:00',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2500)

    @patch('cinema_app.views.messages.error')
    def test_availability_for_unauthorized(self, error):
        request = self.factory.get('movie_details/3/')
        request.user = AnonymousUser()
        response = MovieDetailsView.as_view()(request, pk=3)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_availability_for_authorized(self):
        request = self.factory.get('movie_details/3/')
        request.user = self.user
        response = MovieDetailsView.as_view()(request, pk=3)
        self.assertEqual(response.status_code, 200)

    def test_get_object_method(self):
        request = self.factory.get('movie_details/3/')
        request.user = self.user
        response = MovieDetailsView.as_view()(request, pk=3)
        movie_session_obj = MovieSession.objects.get(id=3)
        self.assertEqual(response.context_data['object'], movie_session_obj)
        self.assertEqual(response.status_code, 200)


class UserProfileViewTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()
        self.user_owner = CustomUser.objects.create_user(id=12, username='user12', email='user12@email.com',
                                                         password='SuperUser12')

        self.user_stranger = CustomUser.objects.create_user(id=13, username='user18', email='user18@email.com',
                                                            password='SuperPas18')

        CinemaHall.objects.create(id=14, hall_name="White", hall_size=100)
        hall = CinemaHall.objects.get(id=14)

        MovieSession.objects.create(
            id=15,
            hall=hall,
            movie_title='TestMovie3',
            movie_description='All about test movie 3',
            session_start_time='08:00',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2000)
        movie_session_1 = MovieSession.objects.get(id=15)

        MovieSession.objects.create(
            id=16,
            hall=hall,
            movie_title='NewTestMovie4',
            movie_description='All about new movie 4',
            session_start_time='10:45',
            session_end_time='12:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=3000)
        movie_session_2 = MovieSession.objects.get(id=16)

        Purchase.objects.create(
            id=1,
            user=self.user_owner,
            movie=movie_session_1,
            purchase_date='2023-08-01',
            purchase_sum=4000,
            quantity=2)

        Purchase.objects.create(
            id=2,
            user=self.user_owner,
            movie=movie_session_2,
            purchase_date='2023-08-01',
            purchase_sum=9000,
            quantity=3)

        self.request = self.factory.get('/profile/')

    def test_availability_for_user_owner(self):
        request = self.request
        request.user = self.user_owner
        response = UserProfileView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        purchase_obj = Purchase.objects.filter(user=self.request.user)
        self.assertQuerysetEqual(purchase_obj, response.context_data['purchase_list'])

    def test_availability_for_user_stranger(self):
        request = self.request
        request.user = self.user_stranger
        response = UserProfileView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        purchase_obj = Purchase.objects.filter(user=self.user_owner)
        self.assertNotEqual(purchase_obj, response.context_data['purchase_list'])

    @patch('cinema_app.views.messages.error')
    def test_availability_for_anonymous_user(self, error):
        request = self.request
        request.user = AnonymousUser()
        response = UserProfileView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

