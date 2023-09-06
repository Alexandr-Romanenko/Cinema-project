from rest_framework.test import APIRequestFactory, APITestCase
from cinema_app.api.serializers import CustomUserSerializer, CinemaHallSerializer, MovieSessionSerializer, \
    PurchaseSerializer
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from freezegun import freeze_time
from datetime import datetime, timedelta


class CustomUserSerializerTestCase(APITestCase):

    def setUp(self):
        CustomUser.objects.create_user(id=1, username='test', email='test@email.com', password='TestPass3')

    def test_valid_registration(self):
        input_data = {'username': 'user', 'email': 'user@email.com', 'password': 'UserPass3'}
        serializer = CustomUserSerializer(data=input_data)
        serializer.is_valid()
        serializer.save()
        expected_data = {'id': 2, 'username': 'user', 'email': 'user@email.com', 'total_sum': 0}
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(CustomUser.objects.filter(email='user@email.com').exists())

    def test_invalid_registration_without_username(self):
        input_data = {'username': '', 'email': 'user1@email.com', 'password': 'UserPass3'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_registration_with_exists_username(self):
        input_data = {'username': 'Test', 'email': 'user2@email.com', 'password': 'UserPass3'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_registration_without_password(self):
        input_data = {'username': 'user1', 'email': 'user3@email.com'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_registration_with_whitespace_in_password(self):
        input_data = {'username': 'user2', 'email': 'user4@email.com', 'password': 'User Pass3'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_registration_with_weak_password(self):
        input_data = {'username': 'user3', 'email': 'user5@email.com', 'password': 'UserPas'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_registration_without_email(self):
        input_data = {'username': 'user4', 'email': ' ', 'password': 'UserPass3'}
        serializer = CustomUserSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())


class CinemaHallSerializerTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        CinemaHall.objects.create(id=1, hall_name="Blue", hall_size=50)
        CinemaHall.objects.create(id=2, hall_name="Orange", hall_size=80)
        hall = CinemaHall.objects.get(id=2)
        movie = MovieSession.objects.create(id=1,
                                            hall=hall,
                                            movie_title="Test busy hall",
                                            movie_description="All about test busy hall",
                                            session_start_time="21:00",
                                            session_end_time="22:00",
                                            session_show_start_date=(datetime.now().date() - timedelta(days=1)),
                                            session_show_end_date=(datetime.now().date() + timedelta(days=6)),
                                            free_seats=hall.hall_size,
                                            ticket_price=500)
        user = CustomUser.objects.create_user(id=2, username='buyer', email='buyer@email.com',
                                              password='UserPass3')
        Purchase.objects.create(id=1, user=user, movie=movie, purchase_date=datetime.now().date(),
                                purchase_sum=1000, quantity=2)

    def test_create_valid_cinema_hall(self):
        input_data = {'hall_name': 'White', 'hall_size': 100}
        request = self.factory.post('/api/cinema_hall/')
        serializer = CinemaHallSerializer(data=input_data, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected_data = {'id': 3, 'hall_name': 'White', 'hall_size': 100}
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(CinemaHall.objects.filter(hall_name='White').exists())

    def test_create_cinema_hall_with_exists_hall_name(self):
        input_data = {'hall_name': 'Blue', 'hall_size': 500}
        request = self.factory.post('/api/cinema_hall/')
        serializer = CinemaHallSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_cinema_hall_with_invalid_hall_name(self):
        input_data = {'hall_name': 'Bl', 'hall_size': 200}
        request = self.factory.post('/api/cinema_hall/')
        serializer = CinemaHallSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_cinema_hall_with_invalid_hall_size(self):
        input_data = {'hall_name': 'Black', 'hall_size': 0}
        request = self.factory.post('/api/cinema_hall/')
        serializer = CinemaHallSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_cinema_hall_without_hall_name(self):
        input_data = {'hall_name': None, 'hall_size': 200}
        request = self.factory.post('/api/cinema_hall/')
        serializer = CinemaHallSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_update_valid_cinema_hall(self):
        input_data = {'hall_name': 'Tomato', 'hall_size': 18}
        request = self.factory.put('/api/cinema_hall/1/')
        hall = CinemaHall.objects.get(id=1)
        serializer = CinemaHallSerializer(data=input_data, instance=hall, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected_data = {'id': 1, 'hall_name': 'Tomato', 'hall_size': 18}
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(CinemaHall.objects.filter(hall_name='Tomato').exists())

    def test_update_cinema_hall_if_it_busy(self):
        input_data = {'hall_name': 'Purl', 'hall_size': 18}
        request = self.factory.put('/api/cinema_hall/2/')
        hall = CinemaHall.objects.get(id=2)
        serializer = CinemaHallSerializer(data=input_data, instance=hall, context={'request': request})
        self.assertFalse(serializer.is_valid())


@freeze_time('2023-08-01')
class MovieSessionSerializerTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        CinemaHall.objects.create(id=1, hall_name="Black", hall_size=30)
        hall = CinemaHall.objects.get(id=1)
        movie = MovieSession.objects.create(id=1,
                                            hall=hall,
                                            movie_title="Test busy movie session",
                                            movie_description="All about test busy movie session",
                                            session_start_time="18:00",
                                            session_end_time="20:00",
                                            session_show_start_date="2023-08-01",
                                            session_show_end_date="2023-08-13",
                                            free_seats=hall.hall_size,
                                            ticket_price=600)
        user = CustomUser.objects.create_user(id=1, username='buyer', email='buyer@email.com',
                                              password='UserPass3')
        Purchase.objects.create(id=1, user=user, movie=movie, purchase_date="2023-08-01",
                                purchase_sum=1200, quantity=2)
        MovieSession.objects.create(id=2,
                                    hall=hall,
                                    movie_title="Test valid update movie session",
                                    movie_description="All about test valid update movie session",
                                    session_start_time="20:30",
                                    session_end_time="22:00",
                                    session_show_start_date="2023-08-01",
                                    session_show_end_date="2023-08-15",
                                    free_seats=hall.hall_size,
                                    ticket_price=700)

    def test_create_valid_movie_session(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test serializer',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '10:00:00',
                      'session_end_time': '11:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-15',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected_data = {'id': 3,
                         'hall': 1,
                         'movie_title': 'Test serializer',
                         'movie_description': 'All about creation tests serializer',
                         'session_start_time': '10:00:00',
                         'session_end_time': '11:00:00',
                         'session_show_start_date': '2023-08-01',
                         'session_show_end_date': '2023-08-15',
                         'free_seats': 30,
                         'ticket_price': 2000}
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(MovieSession.objects.filter(movie_title='Test serializer').exists())

    def test_update_valid_movie_session(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test valid update movie session #2',
                      'movie_description': 'Information about test valid update movie session',
                      'session_start_time': '10:00:00',
                      'session_end_time': '11:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-18',
                      'ticket_price': 2000}
        request = self.factory.put('/api/movie_session/2/')
        movie = MovieSession.objects.get(id=2)
        serializer = MovieSessionSerializer(data=input_data, instance=movie, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected_data = {'id': 2,
                         'hall': 1,
                         'movie_title': 'Test valid update movie session #2',
                         'movie_description': 'Information about test valid update movie session',
                         'session_start_time': '10:00:00',
                         'session_end_time': '11:00:00',
                         'session_show_start_date': '2023-08-01',
                         'session_show_end_date': '2023-08-18',
                         'free_seats': 30,
                         'ticket_price': 2000}
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(MovieSession.objects.filter(movie_title='Test valid update movie session #2').exists())

    def test_create_movie_session_with_invalid_hall(self):
        input_data = {'hall': 111,
                      'movie_title': 'Test create invalid movie session',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '10:00:00',
                      'session_end_time': '11:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-15',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_movie_title(self):
        input_data = {'hall': 1,
                      'movie_title': 'Te',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '07:00:00',
                      'session_end_time': '08:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-09',
                      'ticket_price': 200}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_movie_description(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test serializer',
                      'movie_description': 'Bla Bla',
                      'session_start_time': '07:00:00',
                      'session_end_time': '08:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-09',
                      'ticket_price': 200}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_session_start_time(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test create movie session with invalid session start time',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '10:00:00',
                      'session_end_time': '09:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-15',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_session_end_time(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test create movie session with invalid session end time',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '10:00:00',
                      'session_end_time': '10:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-15',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_session_show_start_date(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test create movie session with invalid session show start date',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '08:00:00',
                      'session_end_time': '10:00:00',
                      'session_show_start_date': '2023-08-02',
                      'session_show_end_date': '2023-08-01',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_session_show_end_date(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test create movie session with invalid session show end date',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '10:00:00',
                      'session_end_time': '10:00:00',
                      'session_show_start_date': '2023-08-02',
                      'session_show_end_date': '2023-08-01',
                      'ticket_price': 2000}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_create_movie_session_with_invalid_ticket_price(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test create movie session with invalid ticket price',
                      'movie_description': 'All about creation tests serializer',
                      'session_start_time': '08:00:00',
                      'session_end_time': '11:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-15',
                      'ticket_price': 0}
        request = self.factory.post('/api/movie_session/')
        serializer = MovieSessionSerializer(data=input_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_update_movie_session_if_it_busy(self):
        input_data = {'hall': 1,
                      'movie_title': 'Test valid update movie session #1 if it busy',
                      'movie_description': 'Information about test valid update movie session #1',
                      'session_start_time': '10:00:00',
                      'session_end_time': '11:00:00',
                      'session_show_start_date': '2023-08-01',
                      'session_show_end_date': '2023-08-18',
                      'ticket_price': 2000}
        request = self.factory.put('/api/movie_session/1/')
        movie = MovieSession.objects.get(id=1)
        serializer = MovieSessionSerializer(data=input_data, instance=movie, context={'request': request})
        self.assertFalse(serializer.is_valid())


@freeze_time('2023-08-01')
class PurchaseSerializerTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        CinemaHall.objects.create(id=1, hall_name="Red", hall_size=20)
        hall = CinemaHall.objects.get(id=1)
        MovieSession.objects.create(id=1,
                                    hall=hall,
                                    movie_title="Purchase Serializer Test Case",
                                    movie_description="All about test purchase serializer",
                                    session_start_time="11:00",
                                    session_end_time="13:00",
                                    session_show_start_date="2023-08-01",
                                    session_show_end_date="2023-08-13",
                                    free_seats=hall.hall_size,
                                    ticket_price=700)
        CustomUser.objects.create_user(id=1, username='buyer1', email='buyer123@email.com',
                                       password='UserPass32')

    def test_create_valid_purchase(self):
        user = CustomUser.objects.get(id=1)
        input_data = {'movie': 1, 'quantity': 4}
        request = self.factory.post('/api/cart/')
        serializer = PurchaseSerializer(data=input_data, context={'request': request, 'user': user})
        expected_data = {'id': 1, 'user': 1, 'movie': 1, 'purchase_date': '2023-08-01',
                         'purchase_sum': 2800, 'quantity': 4}
        serializer.is_valid()
        serializer.save()
        self.assertEqual(serializer.data, expected_data)
        self.assertTrue(Purchase.objects.filter(id=1).exists())

    def test_create_purchase_with_invalid_movie_session(self):
        user = CustomUser.objects.get(id=1)
        input_data = {'movie': 111, 'quantity': 2}
        request = self.factory.post('/api/cart/')
        serializer = PurchaseSerializer(data=input_data, context={'request': request, 'user': user})
        self.assertFalse(serializer.is_valid())

    def test_create_purchase_with_zero_quantity(self):
        user = CustomUser.objects.get(id=1)
        input_data = {'movie': 1, 'quantity': 0}
        request = self.factory.post('/api/cart/')
        serializer = PurchaseSerializer(data=input_data, context={'request': request, 'user': user})
        self.assertFalse(serializer.is_valid())

    def test_create_purchase_with_enormous_quantity(self):
        user = CustomUser.objects.get(id=1)
        input_data = {'movie': 1, 'quantity': 1000}
        request = self.factory.post('/api/cart/')
        serializer = PurchaseSerializer(data=input_data, context={'request': request, 'user': user})
        self.assertFalse(serializer.is_valid())

