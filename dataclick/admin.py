from django.contrib import admin
from .models import Jobs,Genres,Person,PersonImages,TvChannel,Drama,CastOfDrama,Movie,MovieImages
# Register your models here.

admin.site.register(Person)
admin.site.register(PersonImages)
admin.site.register(TvChannel)
admin.site.register(Drama)
admin.site.register(CastOfDrama)
admin.site.register(Movie)
admin.site.register(MovieImages)

admin.site.register(Jobs)
admin.site.register(Genres)

