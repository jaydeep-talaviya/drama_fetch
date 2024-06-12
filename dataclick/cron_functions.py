import requests
from bs4 import BeautifulSoup
import nest_asyncio
from requests_html import HTMLSession
from dataclick.models import *
from datetime import datetime,timedelta
from .helper_functions import *


# get all genre everyday

def get_genre_list(url):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(url)
    html_str = r.text
    soup = BeautifulSoup(html_str, 'html.parser')
    selected_all_genre=soup.find('select',attrs={'name':'genre'})
    all_options=selected_all_genre.find_all('option')
    print("All Genres",all_options)
    for single_option in all_options:
        if single_option.text !="-" and not Genres.objects.filter(genre_name=single_option.text):
            Genres.objects.create(genre_name=single_option.text)

# Get All the compainies
def get_companies_list(url,next_page=None):
    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(next_page if next_page else url)
    html_str = r.text
    soup = BeautifulSoup(html_str, 'html.parser')
    total_companies = soup.find('ul',attrs={'class':'company_list'})
    companies = total_companies.find_all('a')
    for company in companies:
        if company.text.find('Next ›') == -1 and company.text.find('‹ Previous') == -1:
            link = 'https://www.hancinema.net/'+company.attrs.get('href')
            name = company.text
            TvChannel.objects.get_or_create(tv_channel=name,tv_channel_link=link)
        elif company.text.find('Next ›') == 0 and company.text.find('‹ Previous') == -1:
            next_page = 'https://www.hancinema.net/'+ company.attrs.get('href')
            get_companies_list(url,next_page)

#######################################################################3
# get drama links

def get_kdrama_links_all(url, main_search_link):
    nest_asyncio.apply()

    session = HTMLSession()
    r = session.get(main_search_link)
    html_str = r.text
    soup = BeautifulSoup(html_str, 'html.parser')
    links_from_genre = []
    main_content_of_links = soup.find('ul', attrs={'class': 'list work_list'})
    print(main_search_link)
    links_tag_parent = main_content_of_links.find_all('div', attrs={'class': 'work_info_short'})
    for single_link_tag in links_tag_parent:
        airing_dates = single_link_tag.find('span', attrs={'itemprop': 'datePublished'}).text
        # print(airing_dates, "airing_dates")
        links_from_genre.append(single_link_tag.find('a').attrs['href'])

    page_nxt_btn = main_content_of_links.find_next('nav')
    if len(list(filter(lambda x: x.text == "Next ›", page_nxt_btn.find_all('a')))) == 1:
        next_link = list(filter(lambda x: x.text == "Next ›", page_nxt_btn.find_all('a')))[0].attrs['href']
        links_from_genre += get_kdrama_links_all(url, url + next_link)
    return links_from_genre


##########################################################
def get_person_links_all(url,previous_date,today,main_search_link):

    total_kdrama_links=[]
    nest_asyncio.apply()

    session = HTMLSession()
    r = session.get(main_search_link)
    html_str = r.text
    soup = BeautifulSoup(html_str, 'html.parser')
    links_from_genre=[]
    main_content_of_links=soup.find('ul',attrs={'class':'list person_list'})
    links_tag_parent=main_content_of_links.find_all('li')
#     print(links_tag_parent,">>>>>main_content_of_links\n\n\n\n\n")

    for single_link_tag in links_tag_parent:
        current_datetime= datetime.strptime(single_link_tag.find('a').find('strong').text, '%Y/%m/%d')
#         print(current_datetime,previous_date,today)
        if current_datetime >= previous_date and current_datetime <= today:
            links_from_genre.append(single_link_tag.find('a').attrs['href'])
        else:
            return links_from_genre
        
    page_nxt_btn=main_content_of_links.find_next('nav')
    next_link=page_nxt_btn.find_next('a').attrs['href']
    if len(list(filter(lambda x:x.text=="Next ›",page_nxt_btn.find_all('a'))))==1:
        next_link=list(filter(lambda x:x.text=="Next ›",page_nxt_btn.find_all('a')))[0].attrs['href']
        links_from_genre+=get_person_links_all(url,previous_date,today,url+next_link)
    return links_from_genre


#########################################################
# Movie

# get new Movies links

def get_movies_links_all(url,main_search_link):
    nest_asyncio.apply()

    session = HTMLSession()
    r = session.get(main_search_link)
    html_str = r.text
    soup = BeautifulSoup(html_str, 'html.parser')
    links_from_genre=[]
    main_content_of_links=soup.find('ul',attrs={'class':'list work_list'})

    links_tag_parent=main_content_of_links.find_all('div',attrs={'class':'work_info_short'})
    for single_link_tag in links_tag_parent:
        airing_dates = single_link_tag.find('span', attrs={'itemprop': 'datePublished'}).text
        # print(airing_dates, "airing_dates")
        links_from_genre.append(single_link_tag.find('a').attrs['href'])

    page_nxt_btn=main_content_of_links.find_next('nav')
    if len(list(filter(lambda x:x.text=="Next ›",page_nxt_btn.find_all('a'))))==1:
        next_link=list(filter(lambda x:x.text=="Next ›",page_nxt_btn.find_all('a')))[0].attrs['href']
        links_from_genre+=get_movies_links_all(url,url+next_link)
    return links_from_genre


############ single drama save into db $$$$$$$$$$$$$
def get_single_drama_info(base_url,single_drama_link):
    print(" started to get Drama ..",single_drama_link)
    try:
        all_genres=Genres.objects.all()
        nest_asyncio.apply()
        session = HTMLSession()
        r = session.get(base_url+'/'+single_drama_link)
        html_str = r.text

        soup = BeautifulSoup(html_str,'html.parser')

        main_content_div=soup.find('main',attrs={'class':'main'})

        image_div=main_content_div.find('div',attrs={'class':'main_image_work'})

        #image

        main_theme_img='https:'+image_div.find('img').attrs['src']
        main_info_div=main_content_div.find('div',attrs={"class":"work_info"})

        # Name
        drama_name=main_info_div.find('h1').text


        if not Drama.objects.filter(drama_name=drama_name):

            # other names
            other_names=main_info_div.find('h3').text.split("|")
            # genres
            genres_list=list(map(lambda x:x.text,main_info_div.find_all('a',{'itemprop':'genre'})))
            genres=all_genres.filter(genre_name__in=genres_list)


            #directed_by
            synopsis_div=main_info_div.find('div',attrs={'class':'synopsis'})
            directed_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'director'})
        #     directer_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'director'})))

            ############
            directed_by=get_or_save_director(base_url,directed_tag_list)

            # writer by
            written_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'author'})
        #     written_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'author'})))
            written_by=get_or_save_writer(base_url,written_tag_list)

            # TV Channel/Platform:
            tv_channel_list=list(map(lambda x:x.text,synopsis_div.find_all('a',attrs={'itemprop':'provider'})))
            tv_channel_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'provider'})))
            tv_channel=TvChannel.objects.filter(tv_channel=tv_channel_list[0]).first() if tv_channel_list else None

            # Airing dates
            airing_dates=list(map(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'datePublished'})))[0]
            airing_dates_start=airing_dates.split("~")[0]
            airing_dates_end=False
            if len(airing_dates.split("~"))>1:
                airing_dates_end=airing_dates.split("~")[1]
            # Paragraph synopsis
            last_paragraph=''
            try:
        #         print(synopsis_div.find_all('p'))
                last_paragraph=list(filter(lambda x:(x.find('strong') is not None and x.find('strong').text=='Synopsis') or x.text.lower().find('episode')!=-1 or len(x.text) > 200, synopsis_div.find_all('p')))[0]
            except Exception as e:
                pass

            #main_casts
            cast_contents=main_content_div.find('div',{'class':'box cast_box'})
            # main_casts=cast_contents.find('ul',{'class':'list cast'})
            all_casts_div=[]
            try:
                main_casts=cast_contents.find('ul',{'class':'list cast'})
                # main_casts_names
                all_casts_div=main_casts.find_all('div',{'class':'work_info_short'})
            except:
                pass


            cast_actors_names=[]
            cast_actors_link=[]
            cast_actors_names_in_drama=[]
            try:
                cast_actors_names=list(map(lambda x:x.find('a').text,all_casts_div))
            except:
                cast_actors_names=list(map(lambda x:x.find('i').text,all_casts_div))
            try:
                cast_actors_link=list(map(lambda x:base_url+"/"+x.find('a').attrs['href'],all_casts_div))
            except:
                pass
            try:
                cast_actors_names_in_drama=list(map(lambda x:x.find_all('p')[-1].text,all_casts_div))
            except:
                pass


            cast_actors_names=cast_actors_names
            cast_actors_link=cast_actors_link
            cast_actors_names_in_drama=cast_actors_names_in_drama

            # save into db for castof drama
            casts=get_main_cast_info(cast_actors_names,cast_actors_names_in_drama)
            # other_casts_names

            other_cast_info=[]
            try:
                other_casts_link=base_url+"/"+cast_contents.find('h4').find('a').attrs['href']
                other_cast_info=get_extra_cast_info(base_url,other_casts_link)
            except:
                pass        # all_images_for_sintotal_action_dramagle_drama
            image_page_link=base_url+"/"+image_div.find('h4').find('a').attrs['href']

    #       create new drama from here
            drama=Drama(drama_name=drama_name
                        ,image_url=main_theme_img,
                        other_names=other_names,
                        drama_link=str(base_url+'/'+single_drama_link),
                        tv_channel=tv_channel,
                        airing_dates_start=airing_dates_start,
                        airing_dates_end=airing_dates_end,
                        last_paragraph=str(last_paragraph)
                       )

            drama.save()

            if genres:
                drama.genres.add(*genres)
            if directed_by:
                drama.directed_by.add(*directed_by)
            if written_by:
                drama.written_by.add(*written_by)
            if casts:
                drama.casts.add(*casts)
            if other_cast_info:
                drama.extended_casts.add(*other_cast_info)
            drama.save()

            image_of_single_drama=get_all_images_links(drama.id,image_page_link)
            print(" Finished to get Drama ..", single_drama_link)
        else:
            print("Drama already exist",drama_name)
    except Exception as e:
        print("got some error",e)

def get_single_movie_info(base_url,single_movie_link):
    print(" started to get Movie ..",single_movie_link)
    try:
        all_genres=Genres.objects.all()
        nest_asyncio.apply()
        session = HTMLSession()
        r = session.get(single_movie_link)
        html_str = r.text

        soup = BeautifulSoup(html_str,'html.parser')
        main_content_div=soup.find('main',attrs={'class':'main'})
        image_div=main_content_div.find('div',attrs={'class':'main_image_work'})

        #image
        main_theme_img='https:'+image_div.find('img').attrs['src']
        main_info_div=main_content_div.find('div',attrs={"class":"work_info"})
        # Name
        movie_name=main_info_div.find('h1').text

        if not Movie.objects.filter(movie_name=movie_name):

            # other names
            other_names=main_info_div.find('h3').text.split("|")
            # genres
            genres_list=list(map(lambda x:x.text,main_info_div.find_all('a',{'itemprop':'genre'})))
            genres=all_genres.filter(genre_name__in=genres_list)


            #directed_by
            synopsis_div=main_info_div.find('div',attrs={'class':'synopsis'})
            directed_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'director'})

            ############
            directed_by=get_or_save_director(base_url,directed_tag_list)

            # writer by
            written_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'author'})
        #     written_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'author'})))
            written_by=get_or_save_writer(base_url,written_tag_list)

            airing_date=False
            try:
                release=list(filter(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'datePublished'})))
                if release:
                    airing_date=str(release[0]).replace('<span itemprop="datePublished">','').replace("</span>","")

            except Exception as e:
                print(">>>>release",e,release)

            duration=False
            try:
                duration_list=list(filter(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'duration'})))
                print("<<>>>>>>>>",duration_list[0])

                if duration_list:
                    duration=str(duration_list[0]).replace('<span itemprop="duration">','').replace("</span>","")

            except Exception as e:
                print(">>>>duration",e,duration)

            # Paragraph synopsis
            last_paragraph=''
            try:
        #         print(synopsis_div.find_all('p'))
                last_paragraph=list(filter(lambda x:(x.find('strong') is not None and x.find('strong').text=='Synopsis') or x.text.lower().find('episode')!=-1 or len(x.text) > 200, synopsis_div.find_all('p')))[0]
            except Exception as e:
                print(">>>>>last_paragraph",e)
                pass

        #     print(last_paragraph)
            #main_casts
            cast_contents=main_content_div.find('div',{'class':'box cast_box'})
            all_casts_div=[]
            try:
                main_casts=cast_contents.find('ul',{'class':'list cast'})
                # main_casts_names
                all_casts_div=main_casts.find_all('div',{'class':'work_info_short'})
            except:
                pass

            cast_actors_link=[]
            cast_actors_names_in_drama=[]
            try:
        #         cast_actors_names=single_cast.find('a').text
                cast_actors_names=list(map(lambda x:x.find('a').text,all_casts_div))
            except:
                cast_actors_names=list(map(lambda x:x.find('i').text,all_casts_div))
            try:
        #         cast_actors_link=single_cast.find('a').attrs['href']
                cast_actors_link=list(map(lambda x:base_url+"/"+x.find('a').attrs['href'],all_casts_div))

            except:
                pass
            try:
        #         cast_actors_names_in_drama=single_cast.find_all('p')[-2].text
                cast_actors_names_in_drama=list(map(lambda x:x.find_all('p')[-1].text,all_casts_div))

            except:
                pass


            cast_actors_names=cast_actors_names
            cast_actors_link=cast_actors_link
            cast_actors_names_in_drama=cast_actors_names_in_drama

            # save into db for castof drama
            casts=get_main_cast_info(cast_actors_names,cast_actors_names_in_drama)
            # other_casts_names
            # other_casts_link=base_url+"/"+cast_contents.find('h4').find('a').attrs['href']
            other_cast_info=[]
            try:
                other_casts_link=base_url+"/"+cast_contents.find('h4').find('a').attrs['href']
                other_cast_info=get_extra_cast_info(base_url,other_casts_link)
            except:
                pass        # all_images_for_sintotal_action_dramagle_drama
            image_page_link=base_url+"/"+image_div.find('h4').find('a').attrs['href']

            print(other_cast_info,">>>>>>casts")

    #         create new drama from here
            movie=Movie(movie_name=movie_name,
                        image_url=main_theme_img,
                        movie_link=str(base_url+'/'+single_movie_link),
                        other_names=other_names,
                        airing_date=airing_date,
                        duration=duration,
                        last_paragraph=str(last_paragraph)
                       )
            movie.save()

            if genres:
                movie.genres.add(*genres)
            if directed_by:
                movie.directed_by.add(*directed_by)
            if written_by:
                movie.written_by.add(*written_by)
            if casts:
                movie.casts.add(*casts)
            if other_cast_info:
                movie.extended_casts.add(*other_cast_info)
            movie.save()

            image_of_single_drama=get_all_images_links_movie(movie.id,image_page_link)
            print(">>>>>>>>>\n\n",movie)
        else:
            print("Movie already exist",movie_name)
    except Exception as e:
        print("got some error",e)

# all_genres=Genres.objects.all()
# all_channels=TvChannel.objects.all()

def update_single_drama_info(base_url,single_drama_link):
    all_genres=Genres.objects.all()

    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(single_drama_link)
    html_str = r.text
    
    soup = BeautifulSoup(html_str,'html.parser')
    main_content_div=soup.find('main',attrs={'class':'main'})
    image_div=main_content_div.find('div',attrs={'class':'main_image_work'})

    #image
    # main_theme_img='https:'+image_div.find('img').attrs['src']
    main_info_div=main_content_div.find('div',attrs={"class":"work_info"})
    # Name
    drama_name=main_info_div.find('h1').text
    current_drama=Drama.objects.filter(drama_name=drama_name).first()
    if current_drama:
        
        # other names
        other_names=main_info_div.find('h3').text.split("|")
        # genres
        genres_list=list(map(lambda x:x.text,main_info_div.find_all('a',{'itemprop':'genre'})))
        genres=all_genres.filter(genre_name__in=genres_list)
        
        
        #directed_by
        synopsis_div=main_info_div.find('div',attrs={'class':'synopsis'})
        directed_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'director'})
    #     directer_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'director'})))

        ############
        directed_by=get_or_save_director(base_url,directed_tag_list)

        # writer by
        written_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'author'})
    #     written_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'author'})))
        written_by=get_or_save_writer(base_url,written_tag_list)

        # TV Channel/Platform:
        tv_channel_list=list(map(lambda x:x.text,synopsis_div.find_all('a',attrs={'itemprop':'provider'})))
        tv_channel_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'provider'})))
        tv_channel=TvChannel.objects.filter(tv_channel=tv_channel_list[0]).first() if tv_channel_list else None

        # Airing dates
        airing_dates=list(map(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'datePublished'})))[0]
        airing_dates_start=airing_dates.split("~")[0].strip()
        airing_dates_end=False
        if len(airing_dates.split("~"))>1:
            airing_dates_end=airing_dates.split("~")[1].strip()
        # Official Website
        # official_website=''
        # try:
        #     official_website=synopsis_div.find('ul',{'class':'link_list'}).find('a').attrs['href']
        # except:
        #     pass
        # Paragraph synopsis
        last_paragraph=''
        try:
    #         print(synopsis_div.find_all('p'))
            last_paragraph=list(filter(lambda x:(x.find('strong') is not None and x.find('strong').text=='Synopsis') or x.text.lower().find('episode')!=-1 or len(x.text) > 200, synopsis_div.find_all('p')))[0]
        except Exception as e:
            print(">>>>>last_paragraph",e)
            pass

    #     print(last_paragraph)
        #main_casts
        cast_contents=main_content_div.find('div',{'class':'box cast_box'})
        main_casts=cast_contents.find('ul',{'class':'list cast'})
        # main_casts_names
        all_casts_div=main_casts.find_all('div',{'class':'work_info_short'})


        cast_actors_names=[]
        cast_actors_link=[]
        cast_actors_names_in_drama=[]
        try:
    #         cast_actors_names=single_cast.find('a').text
            cast_actors_names=list(map(lambda x:x.find('a').text,all_casts_div)) 
        except:
            cast_actors_names=list(map(lambda x:x.find('i').text,all_casts_div)) 
        try:
    #         cast_actors_link=single_cast.find('a').attrs['href']
            cast_actors_link=list(map(lambda x:base_url+"/"+x.find('a').attrs['href'],all_casts_div)) 

        except:
            pass
        try:
    #         cast_actors_names_in_drama=single_cast.find_all('p')[-2].text
            cast_actors_names_in_drama=list(map(lambda x:x.find_all('p')[-1].text,all_casts_div)) 

        except:
            pass


        cast_actors_names=cast_actors_names
        cast_actors_link=cast_actors_link
        cast_actors_names_in_drama=cast_actors_names_in_drama

        # save into db for castof drama
        casts=get_main_cast_info(cast_actors_names,cast_actors_names_in_drama)
        # other_casts_names
        other_casts_link=base_url+"/"+cast_contents.find('h4').find('a').attrs['href']
        other_cast_info=get_extra_cast_info(base_url,other_casts_link)
        # all_images_for_sintotal_action_dramagle_drama
        image_page_link=base_url+"/"+image_div.find('h4').find('a').attrs['href']
    

#         create new drama from here
        current_drama.drama_name=drama_name
#         current_drama.image_url=main_theme_img
        current_drama.tv_channel=tv_channel
        current_drama.airing_dates_start=airing_dates_start
        current_drama.airing_dates_end=airing_dates_end
        # current_drama.official_website=official_website
        current_drama.last_paragraph=str(last_paragraph)
        current_drama.save()
        

        if genres:
            current_drama.genres.add(*genres)
        if directed_by:
            current_drama.directed_by.add(*directed_by)
        if written_by:
            current_drama.written_by.add(*written_by)
        if casts:
            current_drama.casts.add(*casts)
        if other_cast_info:
            current_drama.extended_casts.add(*other_cast_info)
        current_drama.save()
        
        if current_drama.dramaimages_set.count() == 0:
            image_of_single_drama=get_all_images_links(current_drama.id,image_page_link)

        print("<<<<<updated",">>>>>>casts")


def update_single_movie_info(base_url,single_movie_link):
    all_genres=Genres.objects.all()

    nest_asyncio.apply()
    session = HTMLSession()
    r = session.get(single_movie_link)
    html_str = r.text
    
    soup = BeautifulSoup(html_str,'html.parser')
    main_content_div=soup.find('main',attrs={'class':'main'})
    image_div=main_content_div.find('div',attrs={'class':'main_image_work'})

    #image

    # main_theme_img='https:'+image_div.find('img').attrs['src']
    main_info_div=main_content_div.find('div',attrs={"class":"work_info"})
    # Name
    movie_name=main_info_div.find('h1').text
    current_movie=Movie.objects.filter(movie_name=movie_name).first()
    if current_movie:
    
        # other names
        other_names=main_info_div.find('h3').text.split("|")
        # genres
        genres_list=list(map(lambda x:x.text,main_info_div.find_all('a',{'itemprop':'genre'})))
        genres=all_genres.filter(genre_name__in=genres_list)

        
        #directed_by
        synopsis_div=main_info_div.find('div',attrs={'class':'synopsis'})
        directed_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'director'})
    #     directer_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'director'})))

        ############
        directed_by=get_or_save_director(base_url,directed_tag_list)

        # writer by
        written_tag_list=synopsis_div.find_all('a',attrs={'itemprop':'author'})
    #     written_person_link=list(map(lambda x:base_url+"/"+x.attrs['href'],synopsis_div.find_all('a',attrs={'itemprop':'author'})))
        written_by=get_or_save_writer(base_url,written_tag_list)

        airing_date=False
        try:
            release=list(filter(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'datePublished'})))[0]
            airing_date=str(release).replace('<span itemprop="datePublished">','').replace("</span>","")

        except:
            print(">>>>release",airing_date)
    
        duration=False
        try:
            duration_list=list(filter(lambda x:x.text,synopsis_div.find_all('span',attrs={'itemprop':'duration'})))[0]
#             print(">>>>>>duration_list",duration_list)
            duration=str(duration).replace('<span itemprop="duration">','').replace("</span>","")
                                                 
        except:
            print(">>>>duration",duration)

        # Paragraph synopsis
        last_paragraph=''
        try:
    #         print(synopsis_div.find_all('p'))
            last_paragraph=list(filter(lambda x:(x.find('strong') is not None and x.find('strong').text=='Synopsis') or x.text.lower().find('episode')!=-1 or len(x.text) > 200, synopsis_div.find_all('p')))[0]
        except Exception as e:
            print(">>>>>last_paragraph",e)
            pass

    #     print(last_paragraph)
        #main_casts
        cast_contents=main_content_div.find('div',{'class':'box cast_box'})
        all_casts_div=[]
        try:
            main_casts=cast_contents.find('ul',{'class':'list cast'})
            # main_casts_names
            all_casts_div=main_casts.find_all('div',{'class':'work_info_short'})
        except:
            pass

        cast_actors_names=[]
        cast_actors_link=[]
        cast_actors_names_in_drama=[]
        try:
    #         cast_actors_names=single_cast.find('a').text
            cast_actors_names=list(map(lambda x:x.find('a').text,all_casts_div)) 
        except:
            cast_actors_names=list(map(lambda x:x.find('i').text,all_casts_div)) 
        try:
    #         cast_actors_link=single_cast.find('a').attrs['href']
            cast_actors_link=list(map(lambda x:base_url+"/"+x.find('a').attrs['href'],all_casts_div)) 

        except:
            pass
        try:
    #         cast_actors_names_in_drama=single_cast.find_all('p')[-2].text
            cast_actors_names_in_drama=list(map(lambda x:x.find_all('p')[-1].text,all_casts_div)) 
            
        except:
            pass


        cast_actors_names=cast_actors_names
        cast_actors_link=cast_actors_link
        cast_actors_names_in_drama=cast_actors_names_in_drama

        # save into db for castof drama
        
        casts=get_main_cast_info(cast_actors_names,cast_actors_names_in_drama)
#         print(">>>>>get_main_cast_info",casts)

        # other_casts_names
        other_cast_info=[]
        try:
            other_casts_link=base_url+"/"+cast_contents.find('h4').find('a').attrs['href']
            other_cast_info=get_extra_cast_info(base_url,other_casts_link)
        except:
            pass
        # all_images_for_sintotal_action_dramagle_drama
        image_page_link=base_url+"/"+image_div.find('h4').find('a').attrs['href']
    

#         update new movie from here

        current_movie.movie_name=movie_name
#         current_movie.image_url=main_theme_img
        current_movie.other_names=other_names
        current_movie.airing_date=airing_date
        current_movie.duration=duration
        current_movie.last_paragraph=str(last_paragraph)
        current_movie.save()

        print("step 2",current_movie.airing_date)


        if genres:
            current_movie.genres.add(*genres)
        if directed_by:
            current_movie.directed_by.add(*directed_by)
        if written_by:
            current_movie.written_by.add(*written_by)
        if casts:
            current_movie.casts.add(*casts)
        if other_cast_info:
            current_movie.extended_casts.add(*other_cast_info)
        current_movie.save()       
        
        
        
        if current_movie.movieimages_set.count() == 0:
            image_of_single_drama=get_all_images_links_movie(current_movie.id,image_page_link)
        print(">>>>updated")