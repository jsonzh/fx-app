from django.db import models
from django.utils import timezone

class Currency(models.Model):
	code = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=100)

class Bank(models.Model):
	code = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=100)

class Rate(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
	time = models.DateTimeField(default=timezone.now)
	cash_buying = models.FloatField(null=True,blank=True)
	cash_selling = models.FloatField(null=True,blank=True)
	spot_buying = models.FloatField(null=True,blank=True)
	spot_selling = models.FloatField(null=True,blank=True)

	def get_locale_time(self):
		return timezone.localtime(self.time)
