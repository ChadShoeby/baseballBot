from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class YahooAccount(models.Model):
	yahoo_email = models.CharField(max_length=200)
	yahoo_url = models.CharField(max_length=200)
	yahoo_token = models.CharField(max_length=200)
	
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE
		)
	#remove on delete eventually