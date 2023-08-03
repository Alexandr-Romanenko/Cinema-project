from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages, auth
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from cinema_app.forms import UserCreateForm, CinemaHallCreateForm, MovieSessionForm, PurchaseCreateForm, \
    UserChoiceFilterForm
from cinema_house.settings import SESSION_COOKIE_LIFETIME_FOR_ADMIN, SESSION_COOKIE_LIFETIME


# Create your views here.

class SuperUserRequiredMixin(UserPassesTestMixin):
    """
    A view that checks if the user is a superuser before allowing them to access a protected
    web page. If the user is not a superuser, they will receive a message error.
    """

    def test_func(self):
        """
        A method that checks whether the user is a superuser or not.
        Returns: bool: True if the user is a superuser, False otherwise.
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        A method is required for redirecting in case of an attempt to access certain pages without permission
        :return: redirect to login page
        """
        messages.error(self.request, "You don't have permission to do this!")
        return HttpResponseRedirect('/login/')


class UserLoginRequiredMixin(LoginRequiredMixin):

    def handle_no_permission(self):
        """
        A method is required for redirecting in case of an attempt to access certain pages without authentication
        :return: redirect to login page
        """
        messages.error(self.request, "You are not login")
        return HttpResponseRedirect('/login/')


class RegistrationNewUser(CreateView):
    """
    View for registration of new user page.
    """
    model = CustomUser
    form_class = UserCreateForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')


class LoginUser(LoginView):
    """
    View for user signup.
    Methods:
        form_valid(form): the method was overriden for the following purposes: check the user's activity on the website
         and if it is absent within a minute, the user automatically logs out.
    """
    template_name = 'login.html'
    next_page = '/'

    def form_valid(self, form):
        """
        Called when the form is successfully validated.
        Check the user's and superuser activity on the website
        and if it is absent within a minute (for user) and 540 minutes (for superuser) , the user / superuser
        automatically logs out.
        Args:
            form (SignUpForm): The validated form.
        Returns:
            super().form_valid(form) (HttpResponse): A redirect to the success URL.
        """
        auth.login(self.request, form.get_user())
        if self.request.user.is_superuser:
            self.request.session.set_expiry(SESSION_COOKIE_LIFETIME_FOR_ADMIN)
            return super().form_valid(form)
        else:
            self.request.session.set_expiry(SESSION_COOKIE_LIFETIME)
            return super().form_valid(form)


class LogoutUser(LogoutView):
    """
    View for logout.
    """
    next_page = reverse_lazy('login')


class CinemaHallCreateView(SuperUserRequiredMixin, CreateView):
    """
    View for creating a new Cinema Hall object. Subclasses SuperUserRequiredMixin
    to ensure that only superusers can create Cinema halls.
    """
    model = CinemaHall
    form_class = CinemaHallCreateForm
    success_url = '/cinema_hall/'
    template_name = 'create_cinema_hall.html'

    def get_form_kwargs(self):
        """
        This method redefined to add request into kwargs for their subsequent transmission to
        class CinemaHallCreateForm forms.py module. Request in forms.py module is necessary to work out messages
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class CinemaHallListView(UserLoginRequiredMixin, ListView):
    """
    A view that displays a list of all halls in the system. Subclasses UserLoginRequiredMixin
    to ensure that only authenticated user can view the list of Cinema halls.
    """
    model = CinemaHall
    template_name = 'cinema_hall.html'
    paginate_by = 7
    queryset = CinemaHall.objects.all()


class UpdateCinemaHallView(SuperUserRequiredMixin, UpdateView):
    """
    A view to update a Cinema hall instance in the database. Subclasses SuperUserRequiredMixin
    to ensure that only superusers can update Cinema halls.
    """
    model = CinemaHall
    form_class = CinemaHallCreateForm
    template_name = 'change_hall.html'
    success_url = '/cinema_hall/'
    queryset = CinemaHall.objects.all()

    def get_form_kwargs(self):
        """
        This method redefined to add request into kwargs for their subsequent transmission to
        class CinemaHallCreateForm forms.py module.
        Request in forms.py module is necessary to work out messages
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request, 'pk': self.kwargs['pk']})
        return kwargs


class MovieSessionListView(ListView):
    """
    A view that displays a list of all available movie sessions.
    """
    model = MovieSession
    template_name = 'cinema.html'
    paginate_by = 7
    queryset = MovieSession.objects.all()

    def get_queryset(self):
        """
        This method returns the queryset of Movie sessions filtered according to the user's choice.
        By default, returns the queryset of Movie sessions for today.
        """
        tzn = timezone.now()
        td = timedelta(days=1)

        if self.request.GET.get('session_date') == 'session_today':
            return super().get_queryset().filter(session_show_start_date__lte=tzn, session_show_end_date__gt=tzn)
        elif self.request.GET.get('session_date') == 'session_tomorrow':
            return super().get_queryset().filter(session_show_start_date__lte=tzn + td,
                                                 session_show_end_date__gt=tzn + td)
        return super().get_queryset().filter(session_show_end_date__gt=tzn)

    def get_ordering(self):
        """
        The method is overridden in order to sort the list of Moviesessions depending on the user's choice
        (3 options are available on the main page: sorting by session start time and price ascending and descending)
        :return: the field or fields used to order the queryset.
        """
        filter_by = self.request.GET.get('filter_by')
        if filter_by == 'start':
            self.ordering = ['session_start_time']
        elif filter_by == 'price_as':
            self.ordering = ['ticket_price']
        elif filter_by == 'price_des':
            self.ordering = ['-ticket_price']
        return self.ordering

    def get_context_data(self, **kwargs):
        """
        Adds additional context to the view sorted according to the user's choice.
        Returns: the context dictionary to be used when rendering the template.
        """
        context = super().get_context_data(**kwargs)
        context['sort'] = UserChoiceFilterForm
        return context


class MovieSessionCreateView(SuperUserRequiredMixin, CreateView):
    """
    View for creating a new MovieSession object. Subclasses SuperUserRequiredMixin
    to ensure that only superusers can create MovieSession objects.
    """
    model = MovieSession
    form_class = MovieSessionForm
    success_url = '/'
    template_name = 'create_movie_session.html'

    def get_form_kwargs(self):
        """
        This method redefined to add request into kwargs for their subsequent transmission to
        class MovieSessionForm forms.py module. Request in forms.py module is necessary to work out messages
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        """
        Override the form_valid method to save the form data and create a new
        MovieSession object according to program logic.
        """
        obj = form.save(commit=False)
        hall = CinemaHall.objects.get(id=self.request.POST['hall'])
        obj.free_seats = hall.hall_size
        obj.save()
        return super().form_valid(form=form)

    def form_invalid(self, form):
        """
        If the form is not valid redirects to the page /create_movie_session/
        """
        return HttpResponseRedirect('/create_movie_session/')


class UpdateMovieSessionView(SuperUserRequiredMixin, UpdateView):
    """
    View for changing exists MovieSession object. Subclasses SuperUserRequiredMixin
    to ensure that only superusers can update MovieSession objects.
    """
    model = MovieSession
    form_class = MovieSessionForm
    success_url = '/'
    template_name = 'change_movie_session.html'

    def get_form_kwargs(self):
        """
        This method redefined to add request and pk (id) into kwargs for their subsequent transmission to
        class MovieSessionForm forms.py module.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'pk': self.kwargs['pk']
        })
        return kwargs


class MovieSessionTomorrowListView(ListView):
    """
    A view that displays a list of all available movie sessions for tomorrow.
    Also added the ability to sort as in the class MovieSessionListView.
    """
    model = MovieSession
    template_name = 'movie_session_tomorrow.html'
    extra_context = {"purchase_form": PurchaseCreateForm()}
    paginate_by = 7

    def get_queryset(self):
        tzn = timezone.now()
        td = timedelta(days=1)

        if self.request.GET.get('session_date') == 'session_today':
            return super().get_queryset().filter(session_show_start_date__lte=tzn, session_show_end_date__gt=tzn)
        elif self.request.GET.get('session_date') == 'session_tomorrow':
            return super().get_queryset().filter(session_show_start_date__lte=tzn + td,
                                                 session_show_end_date__gt=tzn + td)
        return super().get_queryset().filter(session_show_end_date__gt=tzn)

    def get_ordering(self):
        filter_by = self.request.GET.get('filter_by')
        if filter_by == 'start':
            self.ordering = ['session_start_time']
        elif filter_by == 'price_as':
            self.ordering = ['ticket_price']
        elif filter_by == 'price_des':
            self.ordering = ['-ticket_price']
        return self.ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = UserChoiceFilterForm
        return context


class PurchaseCreateView(UserLoginRequiredMixin, CreateView):
    """
    A view that responsible for the purchase logic. Subclasses UserLoginRequiredMixin
    to ensure that only authenticated user can create a purchase object.
    """
    http_method_names = ['post']
    form_class = PurchaseCreateForm
    success_url = '/'
    template_name = 'cart.html'

    def get_form_kwargs(self):
        """
        This method redefined to add request and pk (id) into kwargs for their subsequent transmission to
        class PurchaseCreateForm forms.py module.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
           'request': self.request,
           'pk': self.kwargs['pk']
        })
        return kwargs

    def form_valid(self, form):
        """
        Override the form_valid method to save the form data and create a new
        Purchase object according to program logic.
        """
        obj = form.save(commit=False)
        movie = form.movie
        obj.movie = movie
        obj.user = self.request.user
        movie.free_seats -= obj.quantity
        purchase_sum = movie.ticket_price * obj.quantity
        obj.purchase_sum = purchase_sum
        self.request.user.total_sum += purchase_sum
        with transaction.atomic():
            obj.save()
            movie.save()
            self.request.user.save()
        return super().form_valid(form=form)

    def form_invalid(self, form):
        """
        If the form is not valid redirects to the page /create_movie_session/
        """
        return HttpResponseRedirect('/')


class MovieDetailsView(UserLoginRequiredMixin, DetailView):
    """
    A view that displays the details of a single MovieSession.
    A form with a tickets purchase is also available on the page.
    Subclasses UserLoginRequiredMixin to ensure that only authenticated user has access to the page.
    """
    model = MovieSession
    template_name = 'movie_details.html'
    extra_context = {"purchase_form": PurchaseCreateForm()}

    def get_object(self, queryset=None):
        """
        The method overridden to get a specific MovieSession object
        :param queryset:
        :return: MovieSession object
        """
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get('pk') or self.request.GET.get('pk')
        queryset = queryset.filter(pk=pk)
        obj = queryset.get()
        return obj


class UserProfileView(UserLoginRequiredMixin, ListView):
    """
    View for user profile page.
    Subclasses UserLoginRequiredMixin to ensure that only authenticated user has access to the page.
    """
    model = Purchase
    template_name = 'profile.html'
    paginate_by = 7

    def get_queryset(self):
        """
        The method is overridden so that the authenticated user receives information only about himself
        :return: filtered by a specific user queryset
        """
        return super().get_queryset().filter(user=self.request.user)

