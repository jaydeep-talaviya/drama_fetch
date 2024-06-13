from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .models import Jobs,Genres,Person,PersonImages,TvChannel,Drama,CastOfDrama,Movie,MovieImages
from .serializers import (JobsSerializer,GenresSerializer,
                            TvChannelSerializer,PersonSerializer,
                            DramaSerializer,MovieSerializer,PersonDetailSerializer)
from rest_framework import filters
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .helper_functions import is_date
from datetime import datetime,timedelta
from django.db.models import Q,Subquery,OuterRef,Count
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample,OpenApiTypes

# Create your views here.


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 100
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

class JobLists(APIView):

    @extend_schema(
        responses=JobsSerializer,
        parameters=[
            OpenApiParameter(name='limit', description='Number of results to return per page.', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='offset', description='The initial index from which to return the results.',
                             required=False, type=OpenApiTypes.INT),
        ]
    )
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        all_jobs = Jobs.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py

        result_page = paginator.paginate_queryset(all_jobs, request)
        serializer = JobsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class GenresLists(APIView):
    @extend_schema(
        responses=GenresSerializer,
        parameters=[
            OpenApiParameter(name='limit', description='Number of results to return per page.', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='offset', description='The initial index from which to return the results.',
                             required=False, type=OpenApiTypes.INT),
        ]
    )
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        all_genres=Genres.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py
        result_page = paginator.paginate_queryset(all_genres, request)
        serializer = GenresSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TvChannelsLists(APIView):
    @extend_schema(
        responses=TvChannelSerializer,
        parameters=[
            OpenApiParameter(name='limit', description='Number of results to return per page.', required=False,
                             type=OpenApiTypes.INT),
            OpenApiParameter(name='offset', description='The initial index from which to return the results.',
                             required=False, type=OpenApiTypes.INT),
        ]
    )
    def get(self, request, format=None):
        """
        Return a list of all tv channels.
        """
        all_channel=TvChannel.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py
        result_page = paginator.paginate_queryset(all_channel, request)
        serializer = TvChannelSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PersonFilter(django_filters.FilterSet):
    # jobs = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    class Meta:
        model = Person
        fields = ['gender', 'jobs__job_name']

class PersonLists(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    search_fields = ['name','other_names']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = PersonFilter



class DramaFilter(django_filters.FilterSet):
    # airing_dates_start = django_filters.DateFilter(field_name="airing_dates_start", lookup_expr='gte')
    airing_dates_start = django_filters.CharFilter(method='filter_airing_dates_start')
    airing_dates_end= django_filters.CharFilter(method='filter_airing_dates_end')

    def filter_airing_dates_start(self, queryset, value, *args, **kwargs):
        if not value:
            return queryset
        dramas=[i.id for i in queryset.filter(airing_dates_start__gte=args[0]) if is_date(i.airing_dates_start)]
        queryset =Drama.objects.filter(id__in=dramas)
        return queryset

    def filter_airing_dates_end(self, queryset, value, *args, **kwargs):
        if not value:
            return queryset
        dramas=[i.id for i in queryset.filter(airing_dates_start__lte=args[0]) if is_date(i.airing_dates_start)]
        queryset =Drama.objects.filter(id__in=dramas)
        return queryset

    class Meta:
        model = Drama
        fields = ['genres__genre_name', 'tv_channel__tv_channel','airing_dates_start','airing_dates_end']   


class DramaLists(generics.ListAPIView):

    queryset = Drama.objects.all()
    serializer_class = DramaSerializer
    search_fields = ['drama_name','other_names']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = DramaFilter
    ordering = ['-airing_dates_start']


class MovieFilter(django_filters.FilterSet):
    # airing_dates_start = django_filters.DateFilter(field_name="airing_dates_start", lookup_expr='gte')
    airing_dates_start = django_filters.CharFilter(method='filter_airing_dates_start')
    airing_dates_end= django_filters.CharFilter(method='filter_airing_dates_end')

    def filter_airing_dates_start(self, queryset, value, *args, **kwargs):
        if not value:
            return queryset
        movies=[i.id for i in queryset.filter(airing_date__gte=args[0]) if is_date(i.airing_date)]
        queryset =Movie.objects.filter(id__in=movies)
        return queryset

    def filter_airing_dates_end(self, queryset, value, *args, **kwargs):
        if not value:
            return queryset
        movies=[i.id for i in queryset.filter(airing_date__lte=args[0]) if is_date(i.airing_date)]
        queryset =Movie.objects.filter(id__in=movies)
        return queryset

    class Meta:
        model = Movie
        fields = ['genres__genre_name', 'airing_dates_start','airing_dates_end']   


class MovieLists(generics.ListAPIView):

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    search_fields = ['movie_name','other_names']
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = MovieFilter
    ordering = ['-airing_date']


# single all
# single person by id
class SinglePerson(generics.RetrieveAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonDetailSerializer

class SingleDrama(generics.RetrieveAPIView):
    queryset = Drama.objects.all()
    serializer_class = DramaSerializer

class SingleMovie(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


# upcomming movies
class KdramaUpcomingLists(APIView):
    @extend_schema(
        responses=DramaSerializer,
    )
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        all_drama=Drama.objects.filter(Q(airing_dates_start='Upcoming')|Q(airing_dates_end='Upcoming'))
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py
        result_page = paginator.paginate_queryset(all_drama, request)
        serializer = DramaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#  movies
class KdramaNowAiringLists(APIView):
    @extend_schema(
        responses=DramaSerializer,
    )
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        all_drama=Drama.objects.filter(Q(airing_dates_start='Now airing')|Q(airing_dates_end='Now airing'))
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py
        result_page = paginator.paginate_queryset(all_drama, request)
        serializer = DramaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class KdramaRecentlyCompletedLists(APIView):
    @extend_schema(
        responses=DramaSerializer,
    )
    def get(self, request, format=None):
        today=datetime.now()
        date_after_2month = today + timedelta(days = 61)
        """
        Return a list of all users.
        """
        all_drama=Drama.objects.filter(Q(airing_dates_end__lte=today)|Q(airing_dates_end__gte=date_after_2month)|~Q(airing_dates_end=False)|~Q(airing_dates_start=False))
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can also set this in settings.py
        result_page = paginator.paginate_queryset(all_drama, request)
        serializer = DramaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)