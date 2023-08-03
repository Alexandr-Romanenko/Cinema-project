"""
This module contains the Django models used for the cinema_app application.

Models:
CustomUser: Represents the User model which inherits from the Django built-in
            AbstractUser model  in which the total_sum field is added.
CinemaHall: Represents a cinema hall with a name, size (number of seats).
MovieSession: Represents a movie session with a title, description, start / end  time, start / end date,
              ticket price and images.
Purchase: Represents a purchase with a date, sum and quantity (purchased tickets).

"""

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    """
    A custom user model that extends the built-in Django AbstractUser model
    to add additional fields like total_sum.

    Attributes:
        total_sum (PositiveIntegerField): The amount of money that were spent for all the time in the cinema.
    """

    total_sum = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username


class CinemaHall(models.Model):
    """
    This class represents a cinema hall with a hall name and hall size.

    Attributes:
        hall_name = (CharField): The title of the hall
        hall_size = (PositiveIntegerField): Number of seats in cinema hall
    """

    hall_name = models.CharField(max_length=100)
    hall_size = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['hall_name']

    def __str__(self):
        return self.hall_name


class MovieSession(models.Model):
    """
    A class representing a movie session in the cinema.

    Attributes:
        hall (ForeignKey): A foreign key to the hall where movie session translate.
        movie_title (CharField): The title of the movie.
        movie_description (CharField): A movie description.
        session_start_time (TimeField): A session start time.
        session_end_time (TimeField): A session end time.
        session_show_start_date (DateField): A session start date.
        session_show_end_date (DateField): A session end date.
        free_seats (PositiveIntegerField): Indicating the number of seats available in the hall for this session
        ticket_price (PositiveIntegerField): Indicating the price of a ticket for the session
    """

    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    movie_title = models.CharField(max_length=100)
    movie_description = models.CharField(max_length=300)
    session_start_time = models.TimeField(blank=True, null=True)
    session_end_time = models.TimeField(blank=True, null=True)
    session_show_start_date = models.DateField(blank=True, null=True)
    session_show_end_date = models.DateField(blank=True, null=True)
    free_seats = models.PositiveIntegerField(default=0)
    ticket_price = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['session_show_start_date', 'movie_title']

    def __str__(self):
        return self.movie_title


class Purchase(models.Model):
    """
    A class representing the purchase model.

    Attributes:
        user (ForeignKey): A foreign key to the user who buys the ticket.
        movie (ForeignKey): A foreign key to the movie session.
        purchase_date (DateField): A date of purchase.
        purchase_sum (PositiveIntegerField): A purchase amount.
        quantity (PositiveIntegerField): A number of tickets to be purchased.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(MovieSession, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    purchase_sum = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-purchase_date']

