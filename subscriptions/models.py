from django.db import models

# Create your models here.
class Subscription(models.Model):
    title = models.CharField(max_length = 200)
    price = models.IntegerField()
    template_limit = models.IntegerField(help_text="Limit of template creation")
    campaign_limit = models.IntegerField(help_text="Limit of creating campaigns")
    messages_limit = models.IntegerField(help_text="Limit of sending messages")
    features = models.TextField()

    def __str__(self):
        return self.title