from django.db import models

# Create your models here.
class FAQ(models.Model):
    name = models.CharField(max_length = 200)
    email = models.CharField(max_length = 200)
    query = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.query