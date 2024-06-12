from django.db import models
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
# Create your models here.
import requests


class Genres(models.Model):
    genre_name=models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        # db_table='genre'
        verbose_name='Genre'

    def __str__(self):
        return self.genre_name

class TvChannel(models.Model):
    tv_channel=models.CharField(max_length=500,null=True,blank=True)
    tv_channel_link=models.CharField(max_length=250,null=True,blank=True)

    class Meta:
        # db_table='tv_channel'
        verbose_name='TV Channel'

    def __str__(self):
        return self.tv_channel

class CastOfDrama(models.Model):
    cast=models.ForeignKey('Person',on_delete=models.DO_NOTHING,null=True,blank=True)
    cast_name_in_drama=models.CharField(max_length=2000,null=True,blank=True)
    extended_cast=models.BooleanField(default=False)

class Drama(models.Model):
    drama_name=models.CharField(max_length=200,null=True,blank=True)
    image_url = models.URLField(blank=True,null=True)
    other_names=models.CharField(max_length=900,null=True,blank=True)
    genres=models.ManyToManyField(Genres,null=True,blank=True)
    tv_channel=models.ForeignKey(TvChannel,on_delete=models.DO_NOTHING,null=True,blank=True)
    directed_by=models.ManyToManyField('Person',related_name='directors')
    written_by=models.ManyToManyField('Person',related_name='writters')
    casts=models.ManyToManyField('CastOfDrama',related_name='castsofdrama')
    extended_casts=models.ManyToManyField('CastOfDrama',related_name='extendedcasts')
    airing_dates_start=models.CharField(max_length=500,null=True,blank=True)
    airing_dates_end=models.CharField(max_length=500,null=True,blank=True)
    last_paragraph=models.TextField(null=True,blank=True) # contain episodes
    drama_link=models.CharField(max_length=500,null=True,blank=True)

    class Meta:
        # db_table='drama'
        verbose_name='Drama'

    def __str__(self):
        return self.drama_name

class DramaImages(models.Model):
    # image_file = models.ImageField(upload_to='drama_images',blank=True,null=True)
    image_url = models.URLField(blank=True,null=True)
    drama=models.ForeignKey(Drama,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        # db_table='drama_image'
        verbose_name='Drama Image'

    def __str__(self):
        return self.drama.drama_name + "'s image"

class Movie(models.Model):

    movie_name=models.CharField(max_length=200,null=True,blank=True)
    image_url = models.URLField(blank=True,null=True)
    other_names=models.CharField(max_length=900,null=True,blank=True)
    genres=models.ManyToManyField(Genres,null=True,blank=True)
    directed_by=models.ManyToManyField('Person',related_name='directors_of_movie')
    written_by=models.ManyToManyField('Person',related_name='writters_of_movie')
    casts=models.ManyToManyField('CastOfDrama',related_name='casts_of_movie')
    extended_casts=models.ManyToManyField('CastOfDrama',related_name='extendedcasts_of_movie')
    airing_date=models.CharField(max_length=500,null=True,blank=True)
    duration=models.CharField(max_length=500,null=True,blank=True)
    # official_website=models.CharField(max_length=500,null=True,blank=True)
    last_paragraph=models.TextField(null=True,blank=True)
    movie_link=models.CharField(max_length=500,null=True,blank=True)

class MovieImages(models.Model):
    # image_file = models.ImageField(upload_to='movie_images',blank=True,null=True)
    image_url = models.URLField(blank=True,null=True)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE,null=True,blank=True)

class Jobs(models.Model):
    job_name=models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        # db_table='job'
        verbose_name = 'Job'

    def __str__(self):
        return self.job_name

class Person(models.Model):
    gender=[
        ('Male','Male'),
        ('Female','Female')
    ]

    name=models.CharField(max_length=200,null=True,blank=True)
    gender=models.CharField(max_length=10,null=True,blank=True,choices=gender)
    jobs=models.ManyToManyField(Jobs,related_name='jobs')
    other_names=models.CharField(max_length=600,null=True,blank=True)

class PersonImages(models.Model):
    # image_file = models.ImageField(upload_to='person_images',blank=True,null=True)
    image_url = models.URLField(blank=True,null=True)
    person=models.ForeignKey(Person,on_delete=models.CASCADE,null=True,blank=True,related_name='personimages')

