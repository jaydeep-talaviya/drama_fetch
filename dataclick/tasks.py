from __future__ import absolute_import, unicode_literals
from celery import shared_task
import datetime
import time
from .cron_functions import (get_genre_list,get_companies_list,get_kdrama_links_all,
                            get_person_links_all,get_movies_links_all,
                            get_single_drama_info,
                            get_single_movie_info,
                            update_single_drama_info,
                            update_single_movie_info
                            )
from .helper_functions import get_new_person_from_url,is_date
from .models import *
from datetime import datetime,timedelta


@shared_task(name = "print_msg_main")
def print_message(message, *args, **kwargs):
  print(f"Celery is working!! Message is {message}")

@shared_task(name = "get_all_genres_everyday")
def get_new_genre(*args, **kwargs):
    base_url = 'https://www.hancinema.net/all_korean_movies_dramas.php'
    get_genre_list(base_url)
    print(f"All The Genres are Fetched!")

@shared_task(name = "get_all_company_everyday")
def get_new_companies(*args, **kwargs):
    base_url = 'https://www.hancinema.net/korean_entertainment_companies.php'
    get_companies_list(base_url)
    print(f"All The Companies are Fetched!")


@shared_task(name = "get_new_person_everyday")
def get_new_person(*args, **kwargs):
    dynamic_url='https://www.hancinema.net/search_korean_people.php?sort=recently_added'
    previous_date=datetime.today()-timedelta(days=7)
    today=datetime.today()
    base_url='https://www.hancinema.net'
    total_new_links=get_person_links_all(base_url,previous_date,today,dynamic_url)

    for single_person in total_new_links:
        get_new_person_from_url(base_url,base_url+"/"+single_person)
    
    print(f"Got The all New Person from last 7 days!")



@shared_task(name = "get_new_kdrama_everyday")
def get_new_upcomming_kdrama(*args, **kwargs):
    dynamic_url='https://www.hancinema.net/upcoming-korean-dramas.php'
    base_url='https://www.hancinema.net'
    total_new_links=get_kdrama_links_all(base_url,dynamic_url)
    for single_drama in total_new_links:
        get_single_drama_info(base_url,single_drama)

    print(f"Got The all New drama from last 7 days!")


@shared_task(name = "get_all_kdrama_once")
def get_all_kdrama(*args, **kwargs):
    dynamic_url='https://www.hancinema.net/all_korean_dramas.php'
    base_url='https://www.hancinema.net'
    total_new_links=get_kdrama_links_all(base_url,dynamic_url)
    print(" Total Links...",len(total_new_links))
    for single_drama in total_new_links:
        get_single_drama_info(base_url,single_drama)

    print(f"Got The all drama !!! ")


@shared_task(name = "get_new_movie_everyday")
def get_new_movie(*args, **kwargs):
    next_two_year=datetime.today().year+2
    dynamic_url='https://www.hancinema.net/all_korean_movies_dramas.php?srch=1&year_start=1936&year_end='+str(next_two_year)+'&genre=&work_type=movie&sort=recently_added'
    previous_date=datetime.today()-timedelta(days=7)
    today=datetime.today()
    base_url='https://www.hancinema.net'

    total_new_links=get_movies_links_all(base_url,previous_date,today,dynamic_url)
    for single_movie in total_new_links:
        get_single_movie_info(base_url,base_url+"/"+single_movie)

    print(f"Got The all New Movie from last 7 days!")


########### Update $$$$$$$$$$$$$$$$$$$$$44

@shared_task(name = "update_kdrama_everyday")
def update_kdrama(*args, **kwargs):
    base_url='https://www.hancinema.net'
    updatable_kdrama=Drama.objects.all()
    for i in updatable_kdrama:
        start_date =is_date(i.airing_dates_start)
        end_date = is_date(i.airing_dates_end) if airing_dates_end else False
        if not start_date or (i.airing_dates_end != False and not end_date):
            print(base_url,i.drama_link)
            update_single_drama_info(base_url,i.drama_link)

@shared_task(name = "update_movie_everyday")
def update_movie(*args, **kwargs):
    base_url='https://www.hancinema.net'
    updatable_movie=Movie.objects.all()
    for i in updatable_movie:
        result=is_date(i.airing_date)
        if not result:
            print(base_url,i.movie_link)
            update_single_movie_info(base_url,i.movie_link)