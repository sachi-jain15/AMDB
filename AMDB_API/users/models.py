# Import libraries here...
from django.db import models
import uuid
# Create your models here.

# The model below stores the Details of the User
class Users(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    username = models.CharField(max_length=100, unique= True, null=False, blank=False)
    password = models.CharField(max_length=100, null=False, blank=False)
    email_id = models.CharField(max_length=250, null=False, blank=False)
    short_bio = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

# The model below stores the Details of the Access Token
class token(models.Model):
    user_id = models.ForeignKey(Users,on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    last_request_on = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.access_token = uuid.uuid4()

# The model below stores the Details of the Movies.
class movies(models.Model):
    name = models.CharField(max_length=300)
    duration_in_minutes = models.IntegerField(default=120)
    release_date = models.DateTimeField()
    overall_rating = models.DecimalField(decimal_places=2, max_digits=4)
    censor_board_rating = models.CharField(max_length=5)
    profile_pic_url = models.CharField(max_length=300)
    user_id = models.ForeignKey(Users,on_delete=models.CASCADE)

# The model below stores the Details of the Various Genre.
class genre(models.Model):
    name = models.CharField(max_length=200)

# Model for Mapping Table
class moviegenre(models.Model):
    movie_id = models.ForeignKey(movies,on_delete=models.CASCADE)
    genre_id = models.ForeignKey(genre,on_delete=models.CASCADE)

# The model below stores the Details of the Review of Movies.
class reviews(models.Model):
    user_id = models.ForeignKey(Users,on_delete=models.CASCADE)
    movie_id = models.ForeignKey(movies,on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    review = models.CharField(max_length=300)

