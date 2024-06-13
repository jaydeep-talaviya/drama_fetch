from rest_framework.serializers import ModelSerializer,SerializerMethodField,IntegerField,SlugRelatedField
from .models import Jobs,Genres,Person,PersonImages,TvChannel,Drama,CastOfDrama,Movie,MovieImages,DramaImages
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field,extend_schema_serializer

class JobsSerializer(ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'

class GenresSerializer(ModelSerializer):
    class Meta:
        model = Genres
        fields = '__all__'
        
class PersonImagesSerializer(ModelSerializer):
    class Meta:
        model = PersonImages
        fields = ['image_url']


class PersonSerializerForDrama(ModelSerializer):
    class Meta:
        model = Person
        fields = ['id','name','gender']
        
class CastOfDramaSerializer(ModelSerializer):
    cast=PersonSerializerForDrama(read_only=True)
    class Meta:
        model = CastOfDrama
        fields = ['cast','cast_name_in_drama']

class TvChannelSerializer(ModelSerializer):
    class Meta:
        model = TvChannel
        fields = ['id','tv_channel']

class DramaImagesSerializer(ModelSerializer):
    class Meta:
        model = DramaImages
        fields = ['image_url']

class DramaSerializer(ModelSerializer):

    genres=GenresSerializer(read_only=True, many=True)
    directed_by=PersonSerializerForDrama(read_only=True, many=True)
    written_by=PersonSerializerForDrama(read_only=True, many=True)
    casts=CastOfDramaSerializer(read_only=True, many=True)
    extended_casts=CastOfDramaSerializer(read_only=True, many=True)
    tv_channel=TvChannelSerializer(read_only=True)
    dramaimages=DramaImagesSerializer(many=True,source='dramaimages_set')

    class Meta:
        model = Drama
        fields = ['id','drama_name','image_url','other_names','dramaimages','airing_dates_start','airing_dates_end','last_paragraph','tv_channel','genres','directed_by','written_by','casts','extended_casts']

class MovieSerializerForPerson(ModelSerializer):
    genres = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='genre_name'
    )

    class Meta:
        model = Movie
        fields=['movie_name','other_names','image_url','genres']

class MovieSerializerForPerson(ModelSerializer):
    genres=GenresSerializer(read_only=True, many=True)

    class Meta:
        model = Movie
        fields=['id','movie_name','other_names','image_url','airing_date','duration','last_paragraph','genres']

class DramaSerializerForPerson(ModelSerializer):
    genres=GenresSerializer(read_only=True, many=True)

    class Meta:
        model = Drama
        fields=['id','drama_name','other_names','image_url','tv_channel','airing_dates_start','airing_dates_end','last_paragraph','genres']


class PersonSerializer(ModelSerializer):
    # jobs = SerializerMethodField()
    personimages = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='image_url'
    )
    dramas = SerializerMethodField()
    movies = SerializerMethodField()

    jobs = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='job_name'
    )

    class Meta:
        model = Person
        fields = ['id','name','gender','jobs','other_names','personimages','dramas','movies']

    @extend_schema_field(OpenApiTypes.INT)
    def get_dramas(self, obj):
        return obj.get_total_drama()

    @extend_schema_field(OpenApiTypes.INT)
    def get_movies(self, obj):
        return obj.get_total_movie()

class PersonDetailSerializer(ModelSerializer):
    jobs = JobsSerializer(read_only=True, many=True)
    personimages = PersonImagesSerializer(many=True)
    dramas = SerializerMethodField()
    movies = SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'name', 'gender', 'jobs', 'other_names', 'personimages', 'dramas', 'movies']

    @extend_schema_field(MovieSerializerForPerson)
    def get_dramas(self, obj):
        return DramaSerializerForPerson(Drama.objects.filter(
            Q(casts__cast__id=obj.id) | Q(extended_casts__cast__id=obj.id) | Q(directed_by__id=obj.id) | Q(
                written_by__id=obj.id)).distinct(), many=True).data

    @extend_schema_field(MovieSerializerForPerson)
    def get_movies(self, obj):
        # print(">>>>",obj,Movie.objects.filter(Q(casts__cast__id=obj.id)|Q(extended_casts__cast__id=obj.id)|Q(directed_by__id=obj.id)|Q(written_by__id=obj.id)))
        return MovieSerializerForPerson(Movie.objects.filter(
            Q(casts__cast__id=obj.id) | Q(extended_casts__cast__id=obj.id) | Q(directed_by__id=obj.id) | Q(
                written_by__id=obj.id)).distinct(), many=True).data


class MovieImagesSerializer(ModelSerializer):
    class Meta:
        model = MovieImages
        fields = ['image_url']

class MovieSerializer(ModelSerializer):
    genres=GenresSerializer(read_only=True, many=True)
    directed_by=PersonSerializerForDrama(read_only=True, many=True)
    written_by=PersonSerializerForDrama(read_only=True, many=True)
    casts=CastOfDramaSerializer(read_only=True, many=True)
    extended_casts=CastOfDramaSerializer(read_only=True, many=True)
    movieimages=MovieImagesSerializer(many=True,source='movieimages_set')
    class Meta:
        model = Movie
        fields=['id','movie_name','other_names','image_url','movieimages','airing_date','duration','last_paragraph','genres','directed_by','written_by','casts','extended_casts']

        
