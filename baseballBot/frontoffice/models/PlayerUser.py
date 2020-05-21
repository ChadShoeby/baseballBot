from django.db import models
from django.utils import timezone
from frontoffice.models import Team
from django.contrib.auth.models import User

class PlayerUser(User):
#    team = models.ForeignKey(
#    	Team, 
#   	on_delete=models.CASCADE
#  	)
    class Meta:
    	proxy = True
