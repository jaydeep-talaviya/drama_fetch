from django.urls import path
from .views import (JobLists,
                    GenresLists,
                    TvChannelsLists,PersonLists,
                    DramaLists,MovieLists,
                    SinglePerson,SingleDrama,SingleMovie,
                    KdramaUpcomingLists,KdramaNowAiringLists,
                    KdramaRecentlyCompletedLists)

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns=[
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


    path('jobs',JobLists.as_view(),name='all_jobs'),
    path('genres',GenresLists.as_view(),name='all_genres'),
    path('tvchannel',TvChannelsLists.as_view(),name='tv_channel'),
    path('person',PersonLists.as_view(),name='all_person'),
    path('drama',DramaLists.as_view(),name='all_drama'),
    path('movie',MovieLists.as_view(),name='all_movie'),

    path('person/single/<int:pk>',SinglePerson.as_view(),name='single_person'),

    path('drama/single/<int:pk>',SingleDrama.as_view(),name='single_drama'),
    path('movie/single/<int:pk>',SingleMovie.as_view(),name='single_movie'),

    path('drama/upcoming',KdramaUpcomingLists.as_view(),name='upcoming_drama'),
    path('drama/now_airing',KdramaNowAiringLists.as_view(),name='now_airing_drama'),
    path('drama/recently_completed',KdramaRecentlyCompletedLists.as_view(),name='recently_completed'),


]
