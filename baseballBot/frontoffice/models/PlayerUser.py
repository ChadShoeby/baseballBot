from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class PlayerUser(User):
    class Meta:
    	proxy = True
