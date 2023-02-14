from tokenize import Name
from django.db import models

class ImageStorage(models.Model):
    index = models.CharField(max_length=500)
    imagefile = models.FileField(upload_to="media",blank=True, null=True)
    

    def __str__(self):
        return self.index+": "+str(self.imagefile)
