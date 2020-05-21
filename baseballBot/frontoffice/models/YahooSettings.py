from django.db import models
from django.utils import timezone
from frontoffice.models import PlayerUser

class YahooAccount(models.Model):
	yahoo_email = models.CharField(max_length=200)
	yahoo_url = models.CharField(max_length=200)
	yahoo_token = models.CharField(max_length=200)
	
	user = models.ForeignKey(
		PlayerUser,
		on_delete=models.CASCADE
		)
	#remove on delete eventually