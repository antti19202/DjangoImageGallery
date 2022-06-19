from django.db import models
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
import uuid

# Create your models here.


# Kuvan nimi muutetaan 
def upload_path2(instance, image):
    ext = image.split('.')[-1]
    image = "%s.%s" % (uuid.uuid4(), ext)
    return instance.get_upload_path2(image)

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    profile_pic = ProcessedImageField(
        default="profile_pic.png", 
        upload_to=upload_path2,
        processors=[ResizeToFill(420, 420)], 
        format='JPEG')

    def __str__(self):
        return str(self.user)

    # Profiilikuva tallennetaan "profile_pics/käyttäjä/kuvan nimi"
    def get_upload_path2(self, image):
        return str("profile_pics/"+str(self.user)+'/'+image)
    

class Album(models.Model):
    user = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return str(self.title)

    def get_photos(self):
        return Photo.objects.filter(album=self)
    

# Kuvan nimi muutetaan 
def upload_path(instance, image):
    ext = image.split('.')[-1]
    image = "%s.%s" % (uuid.uuid4(), ext)
    return instance.get_upload_path(image)

class Photo(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    slug = models.SlugField(unique=False)
    tags = TaggableManager(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    image = ProcessedImageField(upload_to=upload_path)
    image_thumbnail_small = ImageSpecField(
        source='image', 
        processors=[ResizeToFit(400, 400)], 
        format='JPEG', 
        options={'quality': 90})

    image_thumbnail_large = ImageSpecField(
        source='image', 
        processors=[ResizeToFit(900, 900)], 
        format='JPEG')


    # Kuva tallennetaan "käyttäjä/kuvan nimi"
    def get_upload_path(self, image):
        return str(self.user)+'/'+image

