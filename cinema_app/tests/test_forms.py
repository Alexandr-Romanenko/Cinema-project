from unittest.mock import patch
from django.test import RequestFactory
from freezegun import freeze_time
from django.test import TestCase
from cinema_app.forms import UserCreateForm, CinemaHallCreateForm, MovieSessionForm, PurchaseCreateForm
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase


class UserCreateFormTest(TestCase):
    def setUp(self):
        CustomUser.objects.create(username='test1', email='user1@email.com', password='SuperPass3')

    def test_create_new_user(self):
        form_data = {
            'username': 'test_user',
            'email': 'test_user@email.com',
            'password1': 'SuperPass3',
            'password2': 'SuperPass3'}
        form = UserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_user_with_exists_name(self):
        form_data = {
            'username': 'test1',
            'email': 'best_user@email.com',
            'password1': 'SuperSecretPass',
            'password2': 'SuperSecretPass'}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_user_with_exists_email(self):
        form_data = {
            'username': 'user',
            'email': 'user1@email.com',
            'password1': 'SuperPass123',
            'password2': 'SuperPass123'}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_user_with_exists_email_case_insensitive(self):
        form_data = {
            'username': 'user',
            'email': 'User1@email.com',
            'password1': 'SuperPass123',
            'password2': 'SuperPass123'}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_user_with_invalid_password(self):
        form_data = {
            'username': 'new_user',
            'email': 'new_user@email.com',
            'password1': '123',
            'password2': '123'}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())


class CinemaHallCreateFormTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()

        CinemaHall.objects.create(id=1, hall_name='White', hall_size=300)
        hall = CinemaHall.objects.get(id=1)

        CustomUser.objects.create(id=2, username='test1', email='user1@email.com', password='SuperPass3')
        user = CustomUser.objects.get(id=2)

        MovieSession.objects.create(
            id=3,
            hall=hall,
            movie_title='Movie',
            movie_description='All about movie',
            session_start_time='07:00',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2000)
        movie = MovieSession.objects.get(id=3)

        Purchase.objects.create(id=4, user=user, movie=movie, purchase_date='2023-08-01', purchase_sum=2000, quantity=1)

    def test_create_new_hall(self):
        form_data = {'hall_name': 'White', 'hall_size': 100}
        form = CinemaHallCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    @patch('cinema_app.forms.messages.error')
    def test_prohibition_of_changes_if_the_ticket_to_the_hall_is_purchased(self, error):
        request = self.factory.post('change_hall/1/')
        form_instance = CinemaHall.objects.get(id=1)

        form = CinemaHallCreateForm(data={'id': 1, 'hall_name': 'Green', 'hall_size': 200},
                                    instance=form_instance, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ["Prohibition of changing the hall Error!"]})

    @patch('cinema_app.forms.messages.error')
    def test_create_hall_with_invalid_name(self, error):
        form_data = {'hall_name': 'Wh', 'hall_size': 50}
        request = self.factory.post('create_cinema_hall/')
        form = CinemaHallCreateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'hall_name': ["The hall name Error!"]})

    @patch('cinema_app.forms.messages.error')
    def test_create_hall_with_invalid_size(self, error):
        form_data = {'hall_name': 'White', 'hall_size': 0}
        request = self.factory.post('create_cinema_hall/')
        form = CinemaHallCreateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'hall_size': ["The hall size Error!"]})

    def test_update_exists_hall(self):
        form_data = {'id': 1, 'hall_name': 'Orange', 'hall_size': 100}
        form = CinemaHallCreateForm(data=form_data)
        self.assertTrue(form.is_valid())


class MovieSessionFormTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()

        CinemaHall.objects.create(id=2, hall_name="Purl", hall_size=100)
        hall = CinemaHall.objects.get(id=2)

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

    @freeze_time('2023-08-01')
    def test_create_new_movie_session(self):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'NewMovie',
            'movie_description': 'All about new movie',
            'session_start_time': '15:45',
            'session_end_time': '17:30',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-08',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        form = MovieSessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_overlap_movie_session(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'NewTestMovie',
            'movie_description': 'All about new test movie',
            'session_start_time': '08:00',
            'session_end_time': '10:30',
            'session_show_start_date': '2023-08-03',
            'session_show_end_date': '2023-08-12',
            'free_seats': hall.hall_size,
            'ticket_price': 1000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            '__all__': ["The movie session overlap Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_movie_title(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'T',
            'movie_description': 'All about new movie',
            'session_start_time': '18:00',
            'session_end_time': '18:30',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-08',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'movie_title': ["The movie title Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_movie_description(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'New best movie',
            'movie_description': 'All info',
            'session_start_time': '18:00',
            'session_end_time': '18:30',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-08',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'movie_description': ["The movie description Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_session_start_time(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'New best movie',
            'movie_description': 'All about new movie',
            'session_start_time': '19:00',
            'session_end_time': '18:00',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-08',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'session_start_time': ["The  start time of movie show Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_date(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'New best movie',
            'movie_description': 'All about new movie',
            'session_start_time': '18:00',
            'session_end_time': '19:30',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-07-08',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'session_show_end_date': ["The end date of movie show Error!"],
                                       '__all__': ["The invalid date Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_duration(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'New best movie',
            'movie_description': 'All about new movie',
            'session_start_time': '18:00',
            'session_end_time': '18:00',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-01',
            'free_seats': hall.hall_size,
            'ticket_price': 2000}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            '__all__': ["The  duration of movie show  Error!"], 'session_start_time':
                ["The  start time of movie show Error!"]})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_new_movie_session_with_invalid_price(self, error):
        hall = CinemaHall.objects.get(id=2)
        form_data = {
            'hall': hall,
            'movie_title': 'New best movie',
            'movie_description': 'All about new movie',
            'session_start_time': '16:00',
            'session_end_time': '18:00',
            'session_show_start_date': '2023-08-01',
            'session_show_end_date': '2023-08-08',
            'free_seats': hall.hall_size,
            'ticket_price': 0}
        request = self.factory.post('create_movie_session/')
        form = MovieSessionForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {
            'ticket_price': ["The invalid price Error!"]})


class PurchaseCreateFormTest(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        self.factory = RequestFactory()

        CinemaHall.objects.create(id=1, hall_name='Blue', hall_size=100)
        hall = CinemaHall.objects.get(id=1)

        CustomUser.objects.create(id=2, username='test2', email='user2@email.com', password='SuperPass2')

        MovieSession.objects.create(
            id=3,
            hall=hall,
            movie_title='Movie',
            movie_description='All about movie',
            session_start_time='07:00',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=2000)

    @freeze_time('2023-08-01')
    def test_create_new_purchase_obj(self):
        user = CustomUser.objects.get(id=2)
        request = self.factory.post('cart/3/', {'user': user})
        form = PurchaseCreateForm(data={'quantity': 1}, pk=3, request=request)
        self.assertTrue(form.is_valid())

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_purchase_obj_with_invalid_zero_quantity(self, error):
        user = CustomUser.objects.get(id=2)
        request = self.factory.post('cart/3/', {'user': user})
        form = PurchaseCreateForm(data={'quantity': 0}, pk=3, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'quantity': ['The quantity Error!'], '__all__': ['This field is required!']})

    @freeze_time('2023-08-01')
    @patch('cinema_app.forms.messages.error')
    def test_create_purchase_obj_with_invalid_enormous_quantity(self, error):
        user = CustomUser.objects.get(id=2)
        request = self.factory.post('cart/3/', {'user': user})
        form = PurchaseCreateForm(data={'quantity': 1000}, pk=3, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['The excess of available quantity Error!']})

    @patch('cinema_app.forms.messages.error')
    def test_create_purchase_obj_with_invalid_time(self, error):
        user = CustomUser.objects.get(id=2)
        request = self.factory.post('cart/3/', {'user': user})
        form = PurchaseCreateForm(data={'quantity': 2}, pk=3, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['The expiration time of ticket purchase Error!']})
