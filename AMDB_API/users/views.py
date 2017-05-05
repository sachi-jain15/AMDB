from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from users.models import Users
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
        return Response({"error_message": "Please Choose another Username as User with this Username already exists!"}, status=400)

    new_user = Users.objects.create(name=name, password=make_password(password), short_bio=short_bio, username=username, email_id=email_id)
    new_user.save()
    return Response(UserSerializer(instance=new_user).data, status=200)
