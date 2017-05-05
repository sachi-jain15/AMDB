from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from users.models import Users, token
from datetime import datetime
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializer import UserSerializer


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
