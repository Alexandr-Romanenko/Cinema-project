from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from datetime import date, datetime


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        required=True, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'total_sum')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def validate(self, data):
        if ' ' in data['password']:
            raise ValidationError({'password': "Password must not contain whitespaces"})
        if len(data['password']) < 8:
            raise ValidationError({'password': "Password must be 8 or more symbols"})
        users = CustomUser.objects.filter(username__iexact=data['username'])
        if users.exists():
            raise ValidationError("User with this name already exists")
        if not data['email']:
            raise ValidationError({'email': "Fild email is required"})
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomUserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'total_sum')


class CinemaHallSerializer(serializers.ModelSerializer):
    hall_size = serializers.IntegerField(required=True)

    class Meta:
        model = CinemaHall
        fields = ['id', 'hall_name', 'hall_size']
        read_only_fields = ('id',)

    def validate(self, data):
        try:
            request_method = self.context['request'].method
            if request_method == 'POST':
                exists_hall = CinemaHall.objects.filter(hall_name__iexact=data['hall_name'])
                if exists_hall.exists():
                    raise ValidationError("The hall with this name already exist")
            if len(data['hall_name']) <= 2:
                raise ValidationError({'hall_name': 'The name of hall can`t be less then 2 symbols'})
            if data['hall_size'] <= 0:
                raise ValidationError({'hall_size': 'The hall size must be more then 0'})
            if self.instance:
                cinema_hall = CinemaHall.objects.get(id=self.instance.id)
                busy_hall = Purchase.objects.filter(movie__hall=cinema_hall)
                if busy_hall:
                    raise serializers.ValidationError('Tickets to this hall have already been purchased,\
                                                       no changes can be made!')
        except KeyError:
            raise ValidationError("Required fild is absence!")

        return data


class MovieSessionSerializer(serializers.ModelSerializer):
    hall = serializers.PrimaryKeyRelatedField(queryset=CinemaHall.objects.all(), required=True)
    session_start_time = serializers.TimeField(required=True)
    session_end_time = serializers.TimeField(required=True)
    session_show_start_date = serializers.DateField(required=True)
    session_show_end_date = serializers.DateField(required=True)
    ticket_price = serializers.IntegerField(required=True)

    class Meta:
        model = MovieSession
        fields = ('id', 'hall', 'movie_title', 'movie_description', 'session_start_time', 'session_end_time',
                  'session_show_start_date', 'session_show_end_date', 'free_seats', 'ticket_price')
        read_only_fields = ('id', 'free_seats', )

    def create(self, validated_data):
        validated_data['free_seats'] = CinemaHall.objects.get(id=validated_data['hall'].id).hall_size
        obj = MovieSession.objects.create(**validated_data)
        return obj

    def validate(self, data):
        try:
            hall = CinemaHall.objects.get(id=data.get('hall').id)
            if not hall:
                raise ValidationError("The hall with this id doesn't exist!")

            if len(data['movie_title']) <= 3:
                raise ValidationError({'movie_title': 'The movie title cannot be less then 3 symbol!'})
            if len(data['movie_description']) <= 9:
                raise ValidationError({'movie_description': 'The movie title cannot be less then 9 symbol!'})
            if data['session_show_start_date'] > data['session_show_end_date']:
                raise ValidationError('The session end date cannot be earlier than the session start date!')
            if data['session_show_start_date'] == data['session_show_end_date'] and \
                    data['session_start_time'] >= data['session_end_time']:
                raise ValidationError('The movie must run for a certain amount of time!')
            if data['session_start_time'] >= data['session_end_time']:
                raise ValidationError("The session end time can't be earlier then session start time!")
            if data['session_show_start_date'] < date.today() or data['session_show_end_date'] < date.today():
                raise ValidationError('You create sessions with invalid data!')
            if data['session_show_start_date'] == date.today() and data['session_start_time'] < datetime.now().time():
                raise ValidationError('You create sessions with invalid time!')
            if data['ticket_price'] <= 0:
                raise ValidationError({'ticket_price': 'The ticket price must be more then 0!'})

            enter_session_show_start_date = Q(session_show_start_date__range=(data['session_show_start_date'],
                                                                              data['session_show_end_date']))
            enter_session_show_end_date = Q(session_show_end_date__range=(data['session_show_start_date'],
                                                                          data['session_show_end_date']))
            enter_session_start_time = Q(session_start_time__range=(data['session_start_time'], data['session_end_time']))
            enter_session_end_time = Q(session_end_time__range=(data['session_start_time'], data['session_end_time']))

            movie_session_obj = MovieSession.objects.filter(hall=hall.pk).filter(
                enter_session_show_start_date | enter_session_show_end_date).filter(
                enter_session_start_time | enter_session_end_time).all()
            if movie_session_obj:
                raise ValidationError('Sessions in the same hall cannot overlap!')

            movie_session = self.instance
            purchases = Purchase.objects.filter(movie=movie_session)
            if purchases:
                raise ValidationError('Tickets for this movie session have already been purchased, \
                                      no changes can be made!')
        except KeyError:
            raise ValidationError("Required fild is absence!")

        return data


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)
    movie = serializers.PrimaryKeyRelatedField(queryset=MovieSession.objects.all(), required=True)
    purchase_date = serializers.DateField(required=False)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'movie', 'purchase_date', 'purchase_sum', 'quantity']
        read_only_fields = ('id', )

    def validate(self, data):
        movie = MovieSession.objects.get(id=data.get('movie').id)
        if not movie:
            raise ValidationError("The movie with this id doesn't exist!")
        if data['quantity'] < 1:
            raise serializers.ValidationError({'quantity': 'You must order at least 1 ticket!'})
        if data['quantity'] > movie.free_seats:
            raise serializers.ValidationError({'quantity': 'You have ordered tickets more than free seats!'})
        if movie.session_start_time < datetime.now().time():
            raise serializers.ValidationError({'purchase_date': 'The movie session has already started!'})
        return data

    def create(self, validated_data):
        user = self.context['user']
        validated_data['user'] = user
        purchase_sum = validated_data['quantity'] * validated_data['movie'].ticket_price
        validated_data['purchase_sum'] = purchase_sum
        obj = Purchase.objects.create(**validated_data)
        return obj

    def get_user(self):
        return self.context['request']


class PurchaseReadSerializer(serializers.ModelSerializer):
    user = CustomUserReadSerializer()
    movie = MovieSessionSerializer()

    class Meta:
        model = Purchase
        fields = ['user', 'movie', 'purchase_date', 'purchase_sum', 'quantity']

