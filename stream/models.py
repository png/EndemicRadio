from django.db import models

# Create your models here.
class Picture(models.Model):
    name = models.CharField(max_length=50)
    picture_image = models.ImageField(upload_to='images/')