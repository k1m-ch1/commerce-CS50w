from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name

class ActiveListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    name = models.CharField(max_length=64)
    description = models.TextField()
    is_active = models.BooleanField()
    current_price = models.FloatField()
    photo = models.ImageField(upload_to="image")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    watchers = models.ManyToManyField(User, blank=True, related_name="on_watch", null=True)
    highest_bidder = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}, {self.current_price}"

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    listing = models.ForeignKey(ActiveListing, on_delete=models.CASCADE, related_name="comments")
    
    def __str__(self):
        return f"{self.owner}, {self.listing}"





