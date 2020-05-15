from rest_framework import serializers
from rest_framework import exceptions, response
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from . import models
from rest_framework.response import Response
import random
import string
from datetime import datetime, date
from django.contrib.auth.models import User



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user

                else:
                    msg = "Account deactivated"
                    raise exceptions.ValidationError(msg)
            else:
                try:
                    User = get_user_model()
                    userdata = User.objects.get(email=username)
                    user = authenticate(username=userdata.username, password=password)
                    if user.is_active:
                        data["user"] = user

                    else:
                        msg = "Account deactivated"
                        raise exceptions.ValidationError(msg)
                except Exception as e:
                    msg = "Wrong Credinails"
                    raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide user name and password"
            raise exceptions.ValidationError(msg)
        return data



class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        if username and password and email and first_name:
            pass
        else:
            msg = "Required all specific details"
            a = exceptions.ValidationError(msg)
            return Response('hi')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'],
                                        password=validated_data['password'], first_name=validated_data['first_name'],
                                        )
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name')
        write_only_fields = ('password',)
        

class GetuserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','first_name','email','is_superuser')
        model = User


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Project




class TeamSerializer(serializers.ModelSerializer):
    # team_member = GetuserSerializer()
    # project = ProjectSerializer()
    class Meta:
        fields = '__all__'
        model = models.ProjectTeam


class GetTeamSerializer(serializers.ModelSerializer):
    team_member = GetuserSerializer()
    project = ProjectSerializer()
    class Meta:
        fields = '__all__'
        model = models.ProjectTeam



class TaskSerializer(serializers.ModelSerializer):
    # project_team = TeamSerializer()
    class Meta:
        fields = '__all__'
        model = models.Task

class GetTaskSerializer(serializers.ModelSerializer):
    project_team = GetTeamSerializer()
    class Meta:
        fields = '__all__'
        model = models.Task


class CommentSerializer(serializers.ModelSerializer):
    # user = GetuserSerializer()
    # task = TaskSerializer()
    class Meta:
        fields = '__all__'
        model = models.TaskComments

class GetCommentSerializer(serializers.ModelSerializer):
    user = GetuserSerializer()
    task = TaskSerializer()
    class Meta:
        fields = '__all__'
        model = models.TaskComments


class GetReportSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Reports