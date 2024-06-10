
import requests
from bs4 import BeautifulSoup
import nest_asyncio
from requests_html import HTMLSession
from dataclick.models import *
from datetime import datetime,timedelta
from .models import *
import ast
from dateutil.parser import parse

# for persons $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def get_image_of_single_actor(image_page_url):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(image_page_url)
    html_str = r.text

    soup = BeautifulSoup(html_str, 'html.parser')
    main_div=soup.find('aside')

    # main_ul=main_div.find('ul',attrs={'class':'list person_list photo_list'})
    # image_content_links=main_ul.find_all('a',{'data-fancybox':'gallery'})
    # image_list_of_single_drama=list(map(lambda x:'https:'+x.attrs['href'],image_content_links))
    # total_links_last=7 if len(image_list_of_single_drama) >=7 else len(image_list_of_single_drama)  
    
    main_ul=main_div.find('ul',attrs={'class':'list person_list photo_list'})
    image_content_links=main_ul.find_all('a')
    image_list_of_single_drama=list(map(lambda x:'https:'+x.find('img').attrs['src'],image_content_links))
    total_links_last=7 if len(image_list_of_single_drama) >=7 else len(image_list_of_single_drama)  
    
    return image_list_of_single_drama[0:total_links_last]

def save_single_image_of_person(person_id,image_url):
    person_image=PersonImages(image_url=image_url)
    person_image.person_id=person_id
    person_image.save()
    return person_image

def check_or_save_job(jobs):
    all_jobs=[]
    for i in jobs:
        current_jobs=Jobs.objects.filter(job_name=i).first()
        if not current_jobs:
            new_job=Jobs(job_name=i)
            new_job.save()
            all_jobs.append(new_job)
        else:
            all_jobs.append(current_jobs)
    return all_jobs
        

################################################
def get_new_person_from_url(base_url,single_person_url):
    nest_asyncio.apply()
    session = HTMLSession()
    main_url=single_person_url
    try:
        r = session.get(main_url)
        html_str = r.text
        soup = BeautifulSoup(html_str, 'html.parser')
        main_div=soup.find('main',attrs={'class':'main'})

        name=main_div.find('h1',attrs={'itemprop':'name'}).text
        old_person=Person.objects.filter(name=name).first()
        if not old_person:
    #       images
            image_links=[]
            try:
                image_main_div=main_div.find('div',attrs={'class':'box main_image person'})
                image_page_link_h4=image_main_div.find('h4')
                image_page_link=image_page_link_h4.find('a').attrs['href']

                image_links=get_image_of_single_actor(base_url+"/"+image_page_link)

            except Exception as e:
                pass
            # main_name
            main_info_div=main_div.find('div',attrs={'class':'box work_info'})

            main_gender=''
            
            try:
                main_gender=main_div.find('span',attrs={'itemprop':'gender'}).text
            except:
                pass
            # jobs
            jobs=[]
            try:
                jobs_list=list(map(lambda x:x.text,main_div.find_all('a',attrs={'itemprop':'jobTitle'})))
                jobs=check_or_save_job(jobs_list)

            except:
                pass
            # other names
            other_names:''
            try:
                other_names=main_div.find('p',attrs={'itemprop':'additionalName'})
                other_names=str(other_names).split(":")[-1].replace("</p>","") if str(other_names) else ''
            except Exception as e:
                print(">>>\n",e,'\n')
            # filmography
            

            person=Person(name=name,gender=main_gender,other_names=other_names)
            person.save()
            if jobs:
                person.jobs.add(*jobs)
                person.save()

            if image_links:
                images_of_person=list(map(lambda x:save_single_image_of_person(person.id,x),image_links))

            return person
        else:
            return old_person
    except Exception as e:
        print(">>>>>>e",e,"not found ",main_url)



########### Drama $####3############################

# add CastOfDrama extended

def add_single_cast(cast_dict,extended):
    cast_name=cast_dict['cast_name']
#     cast_link=cast_dict['cast_link']
    cast_role_for_drama=cast_dict['cast_role_for_drama']
#     print(cast_name,"><<s",cast_role_for_drama,"><ASASA")
    if cast_name !='' or cast_role_for_drama !='':
        single_cast=Person.objects.filter(name=cast_name).first()
        old_castof_drama=CastOfDrama.objects.filter(cast=single_cast,cast_name_in_drama=cast_role_for_drama).first()
        if not old_castof_drama:
            castofdrama=CastOfDrama(cast=single_cast,cast_name_in_drama=cast_role_for_drama,extended_cast=extended)
            castofdrama.save()
            return castofdrama
        else:
            return old_castof_drama
    else:
        return None
    
# helper functions
def get_extra_cast_info(base_url,other_casts_link):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(other_casts_link)
    html_str = r.text
    
    extra_cast = BeautifulSoup(html_str, 'html.parser')
    all_casts=extra_cast.find('ul',attrs={'class':'list cast'})
    all_casts_list=all_casts.find_all('div',attrs={'class':'work_info_short'})
    all_cast_info=[]
    for single_cast in all_casts_list:
        cast_name=''
        cast_link=''
        cast_role_for_drama=''
        try:
            cast_name=single_cast.find('a').text
        except:
            pass
        try:
            cast_link=single_cast.find('a').attrs['href']
        except:
            pass
        try:
            cast_role_for_drama=single_cast.find_all('p')[-2].text
        except:
            pass
        
        single_extra_cast=add_single_cast({
            'cast_name':cast_name,
#             'cast_link':base_url+"/"+cast_link,
            'cast_role_for_drama':cast_role_for_drama
        },extended=True)
        if single_extra_cast is not None:
            all_cast_info.append(single_extra_cast)
    return all_cast_info

def get_main_cast_info(cast_actors_names,cast_actors_names_in_drama):
#     print(">>>>>>>",cast_actors_names)
    if cast_actors_names and cast_actors_names_in_drama:
        all_casts=[]
        for j in range(0,len(cast_actors_names)):
            single_cast=Person.objects.filter(name=cast_actors_names[j]).first()
            old_cast= CastOfDrama.objects.filter(cast=single_cast,cast_name_in_drama=cast_actors_names_in_drama[j]).first()
            if not old_cast:
                castofdrama=CastOfDrama(cast=single_cast,cast_name_in_drama=cast_actors_names_in_drama[j],extended_cast=True)
                castofdrama.save()
                all_casts.append(castofdrama)
            else:
                all_casts.append(old_cast)
        return all_casts

# for drama only    
def save_single_image_of_drama(drama_id,single_image_link):
    drama_image=DramaImages(image_url=single_image_link)
    drama_image.drama_id=drama_id
    drama_image.save()
    return drama_image
        
def get_all_images_links(drama_id,image_page_link):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(image_page_link)
    html_str = r.text
    images_main_source = BeautifulSoup(html_str, 'html.parser')
    image_list_of_single_drama=[]
    try:
        image_content_ul=images_main_source.find('ul',{'class':'list person_list photo_list'})
        image_content_links=image_content_ul.find_all('a',{'data-fancybox':'gallery'})
        total_links_last=6 if len(image_content_links) >=6 else len(image_content_links)  
        
        image_list_of_single_drama=list(map(lambda x:save_single_image_of_drama(drama_id,'https:'+x.attrs['href']),image_content_links[0:total_links_last]))
    except Exception as e:
        print(">>>>error",e,"at ",image_page_link)
#     dr.close()
    return image_list_of_single_drama


# MoviesImage
def save_single_image_of_movie(movie_id,single_image_link):
    movie_image=MovieImages(image_url=single_image_link)
    movie_image.movie_id=movie_id
    movie_image.save()
    return movie_image
        
def get_all_images_links_movie(movie_id,image_page_link):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(image_page_link)
    html_str = r.text
    images_main_source = BeautifulSoup(html_str, 'html.parser')
    image_list_of_single_movie=[]
    try:
        image_content_ul=images_main_source.find('ul',{'class':'list person_list photo_list'})
        image_content_links=image_content_ul.find_all('a',{'data-fancybox':'gallery'})
        total_links_last=6 if len(image_content_links) >=6 else len(image_content_links)  
        
        image_list_of_single_movie=list(map(lambda x:save_single_image_of_movie(movie_id,'https:'+x.attrs['href']),image_content_links[0:total_links_last]))
    except Exception as e:
        print(">>>>error",e,"at ",image_page_link)
#     dr.close()
    return image_list_of_single_movie


# add director or get if exist
def get_or_save_director(base_url,list_of_director_tags):
    directed_by=list(map(lambda x:x.text,list_of_director_tags))
    directer_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],list_of_director_tags))
    directors=[]
    for i in range(0,len(directed_by)):
        single_director=Person.objects.filter(name=directed_by[i]).first()
        if not single_director:
            new_director=get_new_person_from_url(base_url,directer_person_link[i])
            directors.append(new_director)
        else:
            directors.append(single_director)
    return directors

# add writer or get if exist
def get_or_save_writer(base_url,list_of_writer_tags):
    written_by=list(map(lambda x:x.text,list_of_writer_tags))
    written_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],list_of_writer_tags))
    writters=[]
    for i in range(0,len(written_by)):
        single_writer=Person.objects.filter(name=written_by[i]).first()
        if not single_writer:
            new_writer=get_new_person_from_url(base_url,written_person_link[i])
            writters.append(new_writer)
        else:
            writters.append(single_writer)
    return writters





def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False