"""
This module contains Django forms used for creating, editing, and validating
users, purchases and cinema-related objects such as movie sessions, halls. It defines the `UserCreateForm`,
`CinemaHallCreateForm`, `MovieSessionForm`, `PurchaseCreateForm`, and UserChoiceFilterForm classes, each of
which is a subclass of Django's `ModelForm` or `Form` class.
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from datetime import date, datetime
from django.db.models import Q
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from cinema_app.exceptions import ValidationError


class UserCreateForm(UserCreationForm):
    """
    A form for user registration.

    Extends Django's built-in "UserCreationForm".
    The form takes the user's username, email, password and password confirmation as input.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
    )

    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        help_texts = {
            'username': None,
            'email': None,
         }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Email is already registered!')
        return email


class CinemaHallCreateForm(forms.ModelForm):
    """
    A form for creating or updating a cinema hall instance.

    Meta:
        model (CinemaHall): The model that this form is based on.
        fields: All fields that are in the CinemaHall model.
    """

    class Meta:
        model = CinemaHall
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Method overridden to add an object to the request when updating the object for subsequent validation
        :param args:
        :param kwargs:
        :return: updated MovieSessionForm
        """
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        if 'pk' in kwargs:
            self.hall_id = kwargs.pop('pk')
        super(CinemaHallCreateForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        The clean method checks:
        1) whether there is a purchase object in a particular hall. If it exists, then validation will fail
         and raise an error the prohibition of any changes;
        2) length of the hall name. If it less the 2 symbols, then validation will fail;
        3) hall size. If it (number of seats) < or = 0, then validation will fail.

        Parameters:
            self: The instance of the CinemaHallCreateForm object.

        Returns:
            The cleaned form data.
        """

        cleaned_data = super().clean()
        hall_name = cleaned_data.get('hall_name')
        hall_size = cleaned_data.get('hall_size')

        if self.instance:
            hall = self.instance
            busy_hall = Purchase.objects.filter(movie__hall=hall)
            if busy_hall:
                self.add_error('__all__', 'Prohibition of changing the hall Error!')
                messages.error(self.request, 'Tickets to this hall have already been purchased, \
                                                          no changes can be made!')

        # hall = self.instance
        # if self.initial:
        #     busy_hall = Purchase.objects.filter(movie__hall=hall)
        #     if busy_hall:
        #         self.add_error('__all__', 'Prohibition of changing the hall Error!')
        #         messages.error(self.request, 'Tickets to this hall have already been purchased, \
        #                                                   no changes can be made!')

        if len(hall_name) <= 2:
            self.add_error('hall_name', 'The hall name Error!')
            messages.error(self.request, 'The name of hall must be more then 2 symbol!')

        if hall_size <= 0:
            self.add_error('hall_size', 'The hall size Error!')
            messages.error(self.request, 'The hall size must be more then 0!')


class MovieSessionForm(forms.ModelForm):
    """
    A form for creating or updating a movie session instance.

    Meta:
        model (MovieSession): The model that this form is based on.
        fields: 'hall', 'movie_title', 'movie_description', 'session_start_time', 'session_end_time',
                  'session_show_start_date', 'session_show_end_date', 'ticket_price'.
        widgets: representation of an HTML input element in time format for form fields
                session_start_time and session_end_time and date format for form fields
                session_show_start_date, session_show_end_date
    """

    class Meta:
        model = MovieSession
        fields = ('hall', 'movie_title', 'movie_description', 'session_start_time', 'session_end_time',
                  'session_show_start_date', 'session_show_end_date', 'ticket_price')

        widgets = {
            'session_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'session_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'session_show_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session_show_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Method overridden to add an object to the request when updating the object for subsequent validation
        :param args:
        :param kwargs:
        :return: updated MovieSessionForm
        """
        if 'request' in kwargs:
            self.request = kwargs.pop('request', None)
        if 'pk' in kwargs:
            self.moviesession_id = kwargs.pop('pk')
        super(MovieSessionForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        The clean method checks:
        1) there is a purchase object for a specific film session. If it exists, then validation will fail
           and raise an error the prohibition of any changes;
        2) length of the movie title. If it less or equal 3 symbols, then validation will fail;
        3) length of the movie description. If it less or equal 9 symbols, then validation will fail;
        4) if session show start date more than session show end date, then validation will fail;
        5) if session show start date equal session show end date and session start time more or equal
           session end time, then validation will fail;
        6) if session start time more or equal session end time, then validation will fail;
        7) if session show start date less than date today or session show end date less than date today,
           then validation will fail;
        8) if session show start date equal date today and session start time less than datetime now,
           then validation will fail;
        9) the ticket price. If it less or equal zero, then validation will fail;
        10) whether a movie session object exists in a particular hall at a particular date and time. If it exists,
            then validation will fail and raise an error prohibiting the creation of a session object
            in this hall at the date and time specified by the superuser;
        Parameters:
            self: The instance of the MovieSessionCreateForm object.
        Returns:
            The cleaned form data.
        """
        cleaned_data = super().clean()
        hall = cleaned_data.get('hall')
        movie_title = cleaned_data.get('movie_title')
        movie_description = cleaned_data.get('movie_description')
        session_start_time = cleaned_data.get('session_start_time')
        session_end_time = cleaned_data.get('session_end_time')
        session_show_start_date = cleaned_data.get('session_show_start_date')
        session_show_end_date = cleaned_data.get('session_show_end_date')
        ticket_price = cleaned_data.get('ticket_price')

        movie_session = self.instance
        purchases = Purchase.objects.filter(movie=movie_session)
        if purchases:
            self.add_error(None, 'Prohibition of changing the movie session Error')
            messages.error(self.request, 'Tickets for this movie session have already been purchased,\
                 no changes can be made!')

        if len(movie_title) <= 3:
            self.add_error('movie_title', 'The movie title Error!')
            messages.error(self.request, 'The movie title cannot be less then 3 symbol!')

        if len(movie_description) <= 9:
            self.add_error('movie_description', 'The movie description Error!')
            messages.error(self.request, 'The movie title cannot be less then 9 symbol!')

        if session_show_start_date > session_show_end_date:
            self.add_error('session_show_end_date', 'The end date of movie show Error!')
            messages.error(self.request, 'The session end date cannot be earlier than the session start date!')

        if session_show_start_date == session_show_end_date and session_start_time >= session_end_time:
            self.add_error(None, 'The  duration of movie show  Error!')
            messages.error(self.request, 'The movie must run for a certain amount of time!')

        if session_start_time >= session_end_time:
            self.add_error('session_start_time', 'The  start time of movie show Error!')
            messages.error(self.request, "The session end time can't be earlier then session start time!")

        if session_show_start_date < date.today() or session_show_end_date < date.today():
            self.add_error(None, 'The invalid date Error!')
            messages.error(self.request, 'You create sessions with invalid date!')

        if session_show_start_date == date.today() and session_start_time < datetime.now().time():
            self.add_error(None, 'The invalid time Error!')
            messages.error(self.request, 'You create sessions with invalid time!')

        if ticket_price <= 0:
            self.add_error('ticket_price', 'The invalid price Error!')
            messages.error(self.request, 'The ticket price must be more then 0!')

        enter_session_show_start_date = Q(session_show_start_date__range=(session_show_start_date,
                                                                          session_show_end_date))
        enter_session_show_end_date = Q(session_show_end_date__range=(session_show_start_date,
                                                                      session_show_end_date))
        enter_session_start_time = Q(session_start_time__range=(session_start_time, session_end_time))
        enter_session_end_time = Q(session_end_time__range=(session_start_time, session_end_time))

        movie_session_obj = MovieSession.objects.filter(hall=hall.pk).filter(
            enter_session_show_start_date | enter_session_show_end_date).filter(
            enter_session_start_time | enter_session_end_time).all()

        if movie_session_obj:
            self.add_error(None, 'The movie session overlap Error!')
            messages.error(self.request, 'Sessions in the same hall cannot overlap!')


class PurchaseCreateForm(forms.ModelForm):
    """
    A form for creating or updating a purchase instance.

    Meta:
        model (Purchase): The model that this form is based on.
        fields: 'quantity'.
    """

    class Meta:
        model = Purchase
        fields = ['quantity', ]

    def __init__(self, *args, **kwargs):
        """
        The method is overridden for the following purposes: the method accepts kwargs from the class PurchaseCreateView
        of the views.py module and adds the request to the PurchaseCreateForm (this way we also get the user),
        and we also add the id (pk) to get the specific movie session object for which the ticket is bought
        :param args:
        :param kwargs:
        :return: updated PurchaseForm
        """

        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        if 'pk' in kwargs:
            self.movie_id = kwargs.pop('pk')
        return super().__init__(*args, **kwargs)

    def clean(self):
        """
        The clean method checks:
        1) quantity of tickets purchased. If there are no tickets purchased, then validation will fail;
        2) in the try block we try to get the movie object
           - if the quantity of purchased tickets is greater than the number of free seats, then validation will fail;
           - if the session start time less than datetime now, then validation will fail;
          Exception block eliminates the occurrence of an error associated with the absence of an MovieSession object
        Parameters:
            self: The instance of the MovieSessionCreateForm object.
        Returns:
            The cleaned form data.
        """
        cleaned_data = super().clean()
        if not cleaned_data.get('quantity'):
            self.add_error('quantity', "The quantity Error!")
            messages.error(self.request, 'You must order at least 1 ticket!')
            raise forms.ValidationError('This field is required!')
        quantity = cleaned_data.get('quantity')
        try:
            movie = MovieSession.objects.get(pk=self.movie_id)
            self.movie = movie
            if quantity > movie.free_seats:
                self.add_error(None, 'The excess of available quantity Error!')
                messages.error(self.request, 'You have ordered tickets more than free seats!')
            if movie.session_start_time < datetime.now().time():
                self.add_error(None, 'The expiration time of ticket purchase Error!')
                messages.error(self.request, 'The movie session has already started!')
        except MovieSession.DoesNotExist:
            self.add_error(None, 'The object existing Error!')
            messages.error(self.request, 'This movie session does not exist!')


class UserChoiceFilterForm(forms.Form):
    """
    The UserChoiceFilterForm is used in the class MovieSessionListView and class MovieSessionTomorrowListView
      of the views.py module to sort the user's choice.
    Sorting can be done by (1) ticket price ascending or (2) descending, (3) session by session start time
    """
    sort_by_ticket_price_ascending = 'price_as'
    sort_by_ticket_price_descending = 'price_des'
    sort_by_session_start_time = 'start'
    sort_movies = [
        (sort_by_session_start_time, 'sort by start session'),
        (sort_by_ticket_price_ascending, 'sort by price ascending'),
        (sort_by_ticket_price_descending, 'sort by price descending')
    ]
    filter_by = forms.ChoiceField(choices=sort_movies)
