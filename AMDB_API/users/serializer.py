# Import commands :-
from rest_framework import serializers
from users.models import Users, movies

# to get user model serialized
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'name', 'username', 'email', 'short_bio', 'created_on', 'updated_on')

# to get movie model serialized
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = movies
        fields = ('name', 'duration_in_minutes', 'release_date', 'overall_rating', 'censor_board_rating', 'profile_pic_url')
