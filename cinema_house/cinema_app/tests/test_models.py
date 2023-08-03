from datetime import date, time
from django.test import TestCase
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from freezegun import freeze_time


class CustomUserTest(TestCase):

    def setUp(self):
        CustomUser.objects.create(username='test1', email='user1@email.com', password='SuperPass3')
        CustomUser.objects.create(username='test2', email='user2@email.com', password='SuperPass2')

    def test_custom_user_model_fields(self):
        custom_user_test1 = CustomUser.objects.get(username='test1')
        custom_user_test2 = CustomUser.objects.get(username='test2')
        self.assertEqual(custom_user_test1.get_username(), "test1")
        self.assertEqual(custom_user_test2.get_username(), "test2")
        self.assertEqual(custom_user_test1.email, 'user1@email.com')
        self.assertEqual(custom_user_test2.email, 'user2@email.com')
        self.assertEqual(custom_user_test1.password, 'SuperPass3')
        self.assertEqual(custom_user_test2.password, 'SuperPass2')


class CinemaHallTestCase(TestCase):

    def setUp(self):
        CinemaHall.objects.create(id=1, hall_name="Orange", hall_size=500)

    def test_create_cinema_hall(self):
        test_hall = CinemaHall.objects.get(hall_name="Orange")
        self.assertEqual(test_hall.hall_name, "Orange")
        self.assertEqual(test_hall.hall_size, 500)


class MovieSessionTestCase(TestCase):

    def setUp(self):
        CinemaHall.objects.create(id=1, hall_name="Orange", hall_size=500)
        test_hall = CinemaHall.objects.get(id=1)
        MovieSession.objects.create(
            id=7,
            hall=test_hall,
            movie_title='TestMovie',
            movie_description='All about test movie',
            session_start_time='07:45',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=test_hall.hall_size,
            ticket_price=2000)

    def test_create_movie_session(self):
        hall = CinemaHall.objects.get(id=1)
        movie_session = MovieSession.objects.get(id=7)
        self.assertEqual(movie_session.hall, hall)
        self.assertEqual(movie_session.movie_title, 'TestMovie')
        self.assertEqual(movie_session.movie_description, 'All about test movie')
        self.assertEqual(movie_session.session_start_time, time.fromisoformat('07:45'))
        self.assertEqual(movie_session.session_end_time,  time.fromisoformat('10:00'))
        self.assertEqual(movie_session.session_show_start_date, date.fromisoformat('2023-08-01'))
        self.assertEqual(movie_session.session_show_end_date, date.fromisoformat('2023-08-08'))
        self.assertEqual(movie_session.free_seats, hall.hall_size)
        self.assertEqual(movie_session.ticket_price, 2000)


class PurchaseTestCase(TestCase):

    @freeze_time('2023-08-01')
    def setUp(self):
        CustomUser.objects.create(username='test1', email='user1@email.com', password='SuperPass3')
        CinemaHall.objects.create(id=2, hall_name="White", hall_size=300)
        hall = CinemaHall.objects.get(id=2)
        MovieSession.objects.create(
            id=7,
            hall=hall,
            movie_title='TestMovie',
            movie_description='All about test movie',
            session_start_time='07:45',
            session_end_time='10:00',
            session_show_start_date='2023-08-01',
            session_show_end_date='2023-08-08',
            free_seats=hall.hall_size,
            ticket_price=3000)

        movie_session = MovieSession.objects.get(id=7)
        Purchase.objects.create(
            id=1,
            user=CustomUser.objects.get(username='test1'),
            movie=movie_session,
            purchase_date='2023-08-01',
            quantity=3,
            purchase_sum=3*movie_session.ticket_price)

    def test_create_purchase(self):
        user = CustomUser.objects.get(username='test1')
        movie = MovieSession.objects.get(id=7)
        purchase_obj = Purchase.objects.get(id=1)
        self.assertEqual(purchase_obj.user, user)
        self.assertEqual(purchase_obj.movie, movie)
        self.assertEqual(purchase_obj.purchase_date, date.fromisoformat('2023-08-01'))
        self.assertEqual(purchase_obj.quantity, 3)
        self.assertEqual(purchase_obj.purchase_sum, 9000)
