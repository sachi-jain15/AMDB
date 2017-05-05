from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from users.models import Users, token, movies, genre, moviegenre, reviews
from datetime import datetime
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializer import UserSerializer, MovieSerializer


@api_view(['POST'])
def user_create(request):
    try:
        name = request.data["name"]
        password = request.data["password"]
        username = request.data["username"]
        short_bio = request.data["short_bio"]
        email_id = request.data["email_id"]
    except KeyError:
        return Response({"error_message": "Error! Please make sure all the Fields are provided properly."}, status=400)

    if len(name) == 0 or name is None:
        return Response({"error_message": "Name field cannot be empty"}, status=400)

    if len(password) < 6 or password is None:
        return Response({"error_message": "Password length cannot be less than 6 characters!"}, status=400)

    does_username = Users.objects.filter(username=username).first()

    if does_username is not None:
        return Response({"error_message": "Please Choose another Username as User with this Username already exists!"},
                        status=400)

    new_user = Users.objects.create(name=name, password=make_password(password), short_bio=short_bio, username=username,
                                    email_id=email_id)
    new_user.save()
    return Response(UserSerializer(instance=new_user).data, status=200)


@api_view(["GET"])
def get_user(request):
    query = request.query_params
    if len(query) == 0:
        user = Users.objects.all()
        return Response(UserSerializer(instance=user, many=True).data, status=200)
    elif 'user_id' in query.keys() and len(query['user_id']) == 0:
        return Response({"error_message": "User ID not found!"}, status=400)
    elif 'user_id' in query.keys() and not query['user_id'][0].isdigit():
        return Response({"error_message": "User ID should be an Integer!"}, status=400)
    elif 'user_id' in query.keys():
        id = int(query['user_id'])
        user = Users.objects.filter(id=id).first()

        if user is None:
            return Response({"error_message": "User not found!"})

        return Response(UserSerializer(instance=user).data, status=200)
    else:
        return Response({"error_message": "User Id not found!"}, status=400)


@api_view(["POST"])
def login(request):
    try:
        username = request.data["username"]
        password = request.data["password"]
    except KeyError:
        return Response({"error_message": "Invalid Username or Password !"}, status=400)

    user = Users.objects.filter(username=username).first()

    if user is None:
        return Response({"error_message": "Invalid Username or Password."}, status=400)

    if user:
        if not check_password(password, user.password):
            return Response({"error_message": "Invalid Username or Password."}, status=400)
        else:
            access_token = token(user_id=user)
            access_token.create_token()
            access_token.save()
            return Response({"access_token": access_token.access_token}, status=200)
    else:
        return Response({'message': "Username or password not provided"}, status=200)


def check_token(request):
    access_token = request.META['HTTP_TOKEN']
    token_exists = token.objects.filter(access_token=access_token, is_valid=True).first()

    if not token_exists:
        return None
    else:
        current_user = token_exists.user_id
        return current_user.username


@api_view(["POST"])
def create_movie(request):
    current_user = check_token(request)

    if current_user is None:
        return Response({"error_message": "Not Authorized for this task!."}, status=400)

    if current_user == 'KeyError':
        return Response({"error_message": "Access Token not found"}, status=400)

    try:
        name = request.data["name"]
        duration_in_minutes = request.data['duration_in_minutes']
        release_date = request.data['release_date']
        censor_board_rating = request.data['censor_board_rating']
        profile_pic_url = request.data['profile_pic_url']
        genres = request.data['genre']

        try:
            duration_in_minutes = int(duration_in_minutes)
        except ValueError:
            return Response({"error_message": "duration in minutes should be in Integer."}, status=400)

        try:
            censor_board_rating = float(censor_board_rating)
        except ValueError:
            return Response({"error_message": "censor board rating should be a Decimal Number."}, status=400)
    except KeyError:
        return Response({"error_message": "Please make sure all fields are provided."}, status=400)

    if len(name) == 0:
        return Response({"error_message": "Name cannot be empty."}, status=400)

    movie_exists = movies.objects.filter(name=name).first()
    if movie_exists:
        return Response({"error_message": "Movie already exists."}, status=400)

    if not release_date:
        return Response({"error_message": "release date cannot be Empty."}, status=400)

    if not censor_board_rating:
        return Response({"error_message": "censor board rating cannot be Empty."}, status=400)

    if not profile_pic_url:
        return Response({"error_message": "profile pic url cannot be Empty."}, status=400)

    if duration_in_minutes <= 0:
        return Response({"error_message": "duration_in_minutes cannot be zero or less than it."}, status=400)

    if len(genres) == 0:
        return Response({"error_message": "Every movie should have atleast one genre."}, status=400)
    try:
        release_date = datetime.strptime(release_date, "%Y-%m-%d")
    except:
        return Response({"error_message": "Please Enter Date in 'yyyy-mm-dd' format"}, status=400)

    movie = movies.objects.create(name=name, duration_in_minutes=duration_in_minutes, release_date=release_date, overall_rating=0, censor_board_rating=censor_board_rating, profile_pic_url=profile_pic_url, user_id=current_user)
    movie.save()

    for i in genres:
        try:
            genre_string = genre.objects.filter(name=i).first()
            moviegenre.objects.create(movie_id=movie, genre_id=genre_string)
        except:
            return Response({"error_message": "Enter a valid Genre."}, status=400)
    return Response(MovieSerializer(instance=movie).data, status=200)


# Endpoint to get the Movies.
@api_view(["GET"])
def list_movie(request):

    query = request.query_params

    if len(query) == 0:
        movie = movies.objects.all()
        return Response(MovieSerializer(instance=movie, many=True).data, status=200)

    elif 'q' in query.keys() and len(query['q']) == 0:
        return Response({"error_message": "query parameter 'q' not found while processing GET request!"}, status=400)

    elif 'q' in query.keys():
        search = str(query['q'])

        movie = movies.objects.filter(name__icontains=search)

        genre_movie = genre.objects.filter(name__icontains=search)

        movie_list = []
        movie_list_names = []

        if genre_movie is not None:
            for each_genre in genre_movie:
                id = each_genre.id
                movie_for_genre = moviegenre.objects.filter(genre_id=id)

                for i in movie_for_genre:
                    movie_list.append(MovieSerializer(instance=i.movie_id).data)
                    movie_list_names.append(i.movie_id.name)

        if movie is not None:
            for each_movie in movie:
                if each_movie.name not in movie_list_names:
                    movie_list.append(MovieSerializer(instance=each_movie).data)
                    movie_list_names.append(each_movie.name)

        if len(movie_list) == 0:
            return Response({"error_message": "No Movies found!"})

        return HttpResponse(json.dumps(movie_list, indent=4))

    else:
        return Response({"error_message": "query parameter 'q' containing search word not found"}, status=400)



# Endpoint to Review a Movie.
@api_view(["POST"])
def review_movie(request):
    current_user = check_token(request)

    if current_user is None:
        return Response({"error_message": "You are not Authorized to perform this Action."}, status=400)

    if current_user == 'KeyError':
        return Response({"error_message": "Access Token not found"}, status=400)

    try:
        movie_name = request.data["movie_name"]
        rating = request.data["rating"]
        review = request.data["review"]
    except KeyError:
        return Response({"error_message": "Please make sure you provide all fields"}, status=400)

    movie = movies.objects.filter(name=movie_name).first()

    if movie is None:
        return Response({"error_message": "No such movie exists."}, status=400)

    movie_id = int(movie.id)

    try:
        rating = float(rating)
    except ValueError:
        return Response({"error_message": "Rating must be a Number."}, status=400)

    if rating < 0 or rating >= 5:
        return Response({"error_message": "Rating must be between 0 and 5"}, status=400)

    review_exists = reviews.objects.filter(user_id=current_user.id, movie_id=movie.id).first()

    if review_exists:
        return Response({"error_message": "You have already reviewed this movie."}, status=400)

    make_review = reviews.objects.create(user_id=current_user, movie_id=movie, rating=rating, review=review)
    make_review.save()

    reviews_of_movie = reviews.objects.filter(movie_id=movie_id)

    overall_rating = 0

    for each_movie in reviews_of_movie:
        overall_rating += each_movie.rating

    overall_rating /= len(reviews_of_movie)

    movies.objects.filter(id=movie_id).update(overall_rating=overall_rating)
    return Response({"success": "Movie Reviewed"}, status=200)


# Endpoint for Logout.
@api_view(["POST"])
def logout(request):
    current_user = check_token(request)

    if current_user is None:
        return Response({"error_message": "Access Token is Invalid."}, status=400)

    if current_user == 'KeyError':
        return Response({"error_message": "Access Token not found in Header.Please pass it as 'token'"}, status=400)

    access_token = request.META['HTTP_TOKEN']
    cur_token = token.objects.filter(access_token=access_token).first()
    cur_token.is_valid = 0
    cur_token.save()
    return Response({"success": "User Logged Out."}, status=200)