from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=200)
    project_details = models.TextField()
    is_completed = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project,on_delete=models.PROTECT)
    team_member = models.ForeignKey(User,on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.project.project_name) + " - " + str(self.team_member.first_name)  
    
    class Meta:
        unique_together = ('project', 'team_member')


class Task(models.Model):
    project_team = models.ForeignKey(ProjectTeam,on_delete=models.PROTECT)
    title = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=100,default="Assigned") #Assigned,Attenting,ReadyForReview,Completed
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskComments(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    task = models.ForeignKey(Task,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Reports(models.Model):
    report_file = models.FileField()
    from_date = models.DateField()
    date =models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)








