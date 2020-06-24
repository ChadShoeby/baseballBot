from django.db import models
from django.contrib.auth.models import User

from frontoffice.models import League

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, related_name='manager_profile', on_delete=models.CASCADE,null=True)
