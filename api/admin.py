from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Project)
admin.site.register(models.ProjectTeam)
admin.site.register(models.Task)
admin.site.register(models.TaskComments)
admin.site.register(models.Reports)