from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from . import serializers
from django.contrib.auth import login, logout
from rest_framework.authtoken.views import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.permissions import BasePermission
from rest_framework import viewsets
from . import models
from datetime import date
import datetime
import xlsxwriter

# Create your views here.

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user
        else:
            return request.user and request.user.is_superuser


class Ping(APIView):
    def get(self, request, format='json'):
        return Response(status.HTTP_200_OK)


class Login(APIView):
    def post(self, request):
        msg = False
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        try:
            user = serializer.validated_data["user"]
            userobj = User.objects.get(id=user.id)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            dat = {'token': token.key,"user":{'id':userobj.id,'name':userobj.first_name,'email':userobj.email,'is_superuser':userobj.is_superuser}}
            stat = status.HTTP_200_OK
            msg = True
        except Exception as e:
            msg = False
            dat = None
            stat = status.HTTP_400_BAD_REQUEST

        return Response({'success': msg, 'data': dat, 'errors': serializer.errors}, status=stat)


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # simply delete the token to force a
        try:
            request.user.auth_token.delete()
            logout(request)
            msg = True
            error = None
            stat = status.HTTP_200_OK
        except Exception as e:
            msg = False
            error = ["no user/token found", str(e)]
            stat = status.HTTP_400_BAD_REQUEST
        return Response({'success': msg, 'data': {}, 'errors': {'details': error}}, status=stat)




class Projects(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,IsSuperUser)
    queryset = models.Project.objects.all().order_by('-id')
    serializer_class = serializers.ProjectSerializer
    def list(self, request):
        if request.user.is_superuser is True:
            queryset = models.Project.objects.all().order_by('-id')
        else:
            myproject = models.ProjectTeam.objects.filter(team_member_id=request.user.id).only('project_id')
            plist = [n.project_id for n in myproject]
            queryset = models.Project.objects.filter(id__in=plist).order_by('-id')
        
        serializer = serializers.ProjectSerializer(queryset, many=True)
        return Response(data=serializer.data)
     


class Users(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,IsSuperUser)
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = serializers.RegisterSerializer


class Team(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,IsSuperUser)
    queryset = models.ProjectTeam.objects.all()
    serializer_class = serializers.TeamSerializer
    def list(self, request):
        project = request.GET.get('project', None)
        queryset = models.ProjectTeam.objects.all()
        if project:
            queryset = queryset.filter(project_id=project)
        serializer = serializers.GetTeamSerializer(queryset, many=True)
        return Response(data=serializer.data)


class Task(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.Task.objects.all().order_by('-id')
    serializer_class = serializers.TaskSerializer
    def list(self, request):
        project = request.GET.get('project', None)
        team = request.GET.get('team', None)
        queryset = models.Task.objects.all().order_by('-id')
        if project:
            queryset = queryset.filter(project_team__project_id=project)
        if team:
            queryset = queryset.filter(project_team__team_member_id=team)
        serializer = serializers.GetTaskSerializer(queryset, many=True)
        return Response(data=serializer.data)

     


class Comment(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = models.TaskComments.objects.all()
    serializer_class = serializers.CommentSerializer
    def list(self, request):
        task = request.GET.get('task', None)
        queryset = models.TaskComments.objects.all()
        if task:
            queryset = queryset.filter(task_id=task)
        else:
            queryset = None
        serializer = serializers.GetCommentSerializer(queryset, many=True)
        return Response(data=serializer.data)


class ListUsers(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        queryset = User.objects.filter(is_superuser=False)
        serializer = serializers.GetuserSerializer(queryset, many=True)
        return Response(data=serializer.data)



class GetTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request,id):
        queryset = models.Task.objects.get(id=id)
        serializer = serializers.GetTaskSerializer(queryset, many=False)
        return Response(data=serializer.data)

    def put(self,request,id,status):
        try:
            suc = True
            queryset = models.Task.objects.get(id=id)
            queryset.status = status
            if str(status) == "Completed":
                queryset.is_completed = True
            else:
                queryset.is_completed = False
            queryset.save()
        except:
            suc =False
        return Response({'success':suc})


class PStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,IsSuperUser)
    def put(self,request,id):
        try:
            suc = True
            msg = "success"
            queryset = models.Project.objects.get(id=id)
            rel = models.Task.objects.filter(is_completed=True,project_team__project_id=id)
            if rel.count() is 0:
                queryset.is_completed = True
                queryset.save()
            else:
                suc = False
                msg = "Tasks are Pending to Complete"
        except:
            suc =False
            msg = "failed"
        return Response({'success':suc,'msg':msg})


class DashCount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        projects = models.Project.objects.all()
        tasks = models.Task.objects.all()
        if request.user.is_superuser is False:
            tasks = tasks.filter(project_team__team_member_id=request.user.id)
            myproject = models.ProjectTeam.objects.filter(team_member_id=request.user.id).only('project_id')
            plist = [n.project_id for n in myproject]
            projects = projects.filter(id__in=plist)
        data = {'total_projects':projects.count(),"total_tasks":tasks.count(),'completed_projects':projects.filter(is_completed=True).count(),
            "pending_projects":projects.filter(is_completed=False).count(),'completed_tasks':tasks.filter(is_completed=True).count(),
            'pending_tasks':tasks.filter(is_completed=False).count()}
        return Response({"data":data})


class Report(APIView):
    def get(self,request):
        if date.today().weekday() == 4:
            users = User.objects.filter(is_superuser=False)
            today = datetime.datetime.today().date()
            sevendays = today - datetime.timedelta(days=7)
            try:
                file = models.Reports.objects.get(from_date=sevendays)
                suc = False
            except:
                filename = 'media/EMRPT-'+str(sevendays)+'-'+str(datetime.datetime.today().date())+'.xlsx'
                name = 'EMRPT-'+str(sevendays)+'-'+str(datetime.datetime.today().date())+'.xlsx'
                workbook = xlsxwriter.Workbook(filename)
                worksheet = workbook.add_worksheet('Report-'+str(sevendays)+"-"+str(today))
                worksheet.write(0, 0, 'EMPLOYEE ID')
                worksheet.write(0, 1,'EMPLOYEE NAME')
                worksheet.write(0, 2, 'EMAIL')
                worksheet.write(0, 3, 'Total Tasks')
                worksheet.write(0, 4, 'Completed')
                worksheet.write(0, 5, 'Pending')
                p = 1
                for i in users:
                    usertasks = models.Task.objects.filter(project_team__team_member_id=i.id,created_at__gte=sevendays)
                    worksheet.write(p,0,"EMPID"+str(i.id))
                    worksheet.write(p,1,str(i.first_name))
                    worksheet.write(p,2,str(i.email))
                    worksheet.write(p,3,str(usertasks.count()))
                    worksheet.write(p,4,str(usertasks.filter(is_completed=True).count()))
                    worksheet.write(p,5,str(usertasks.filter(is_completed=False).count()))
                    p = p + 1
                workbook.close()
                dat = models.Reports()
                dat.report_file = name
                dat.from_date = sevendays
                dat.save()
                suc = True




        else:
            suc =False


        return Response({"success":suc})
    

class GetReport(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,IsSuperUser)
    queryset = models.Reports.objects.all().order_by('-id')
    serializer_class = serializers.GetReportSerializer