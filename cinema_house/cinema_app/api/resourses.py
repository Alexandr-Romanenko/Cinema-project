from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from cinema_app.api.serializers import CustomUserSerializer, CinemaHallSerializer, MovieSessionSerializer, \
    PurchaseSerializer, PurchaseReadSerializer
from cinema_app.models import CustomUser, CinemaHall, MovieSession, Purchase
from django.db import transaction
from cinema_app.api.permissions import IsObjectOwnerOrAdmin, IsAdminOrReadOnly
from datetime import date, timedelta


class LogoutApiView(APIView):

    def post(self, request, *args, **kwargs):
        token: Token = request.auth
        token.delete()
        return Response('You have successfully completed your session!')


class CustomUserCreateAPIView(CreateAPIView):
    permission_classes = [IsObjectOwnerOrAdmin]
    queryset = CustomUser.objects.all()
    http_method_names = ['post', ]
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return super().get_permissions()


class CinemaHallViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class MovieSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = MovieSession.objects.filter(session_show_end_date__gt=timezone.now())
    serializer_class = MovieSessionSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_queryset(self):
        if len(self.request.GET.keys()) == 0:
            queryset = self.queryset
            return queryset

        session_start_time = self.request.query_params.get('session_start_time') or '00:00:00'
        session_end_time = self.request.query_params.get('session_end_time') or '23:59:59'
        hall = self.request.query_params.get('hall_id')
        session_show_day = self.request.query_params.get('day')
        time_range = Q(session_start_time__range=(session_start_time, session_end_time))

        if session_show_day == 'today':
            return super().get_queryset().filter(session_show_start_date__lte=date.today(),
                                                 session_show_end_date__gt=date.today())

        elif session_show_day == 'tomorrow':
            return super().get_queryset().filter(session_show_start_date__lte=date.today() + timedelta(days=1),
                                                 session_show_end_date__gt=date.today())

        if hall:
            return super().get_queryset().filter(time_range, session_show_start_date__lte=date.today(),
                                                 session_show_end_date__gte=date.today(),
                                                 hall_id=hall)


class PurchaseCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Purchase.objects.all()
    http_method_names = ['post', ]
    serializer_class = PurchaseSerializer

    def get_serializer_context(self):
        context = super(PurchaseCreateAPIView, self).get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def perform_create(self, serializer):
        serializer.validated_data['movie'].free_seats -= serializer.validated_data['quantity']
        self.request.user.total_sum += serializer.validated_data['movie'].ticket_price * \
                                       serializer.validated_data['quantity']
        with transaction.atomic():
            self.request.user.save()
            serializer.validated_data['movie'].save()
            serializer.save()


class ProfileApiView(ListAPIView):
    permission_classes = [IsObjectOwnerOrAdmin]
    queryset = Purchase.objects.all()
    serializer_class = PurchaseReadSerializer

    def get_queryset(self):
        return self.queryset.all() if self.request.user.is_superuser else self.queryset.filter(user=self.request.user)




