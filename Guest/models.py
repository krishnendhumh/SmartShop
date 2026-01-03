from django.db import models
from Admin.models import *

# Create your models here.
class tbl_user(models.Model):
    user_name=models.CharField(max_length=50)
    user_email=models.CharField(max_length=50)
    user_contact=models.CharField(max_length=50)
    user_address=models.CharField(max_length=50)
    user_photo=models.FileField(upload_to="Assets/UserDocs/")
    user_password=models.CharField(max_length=50)
    place = models.ForeignKey(tbl_place,on_delete=models.CASCADE)

class tbl_shop(models.Model):
    shop_name=models.CharField(max_length=50)
    shop_email=models.CharField(max_length=50)
    shop_contact=models.CharField(max_length=50)
    shop_address=models.CharField(max_length=50)
    shop_photo=models.FileField(upload_to="Assets/ShopDocs/")
    shop_proof=models.FileField(upload_to="Assets/ShopDocs/")
    shop_password=models.CharField(max_length=50)
    shop_status=models.IntegerField(default=0)
    place = models.ForeignKey(tbl_place,on_delete=models.CASCADE)

class tbl_deliveryboy(models.Model):
    delboy_name=models.CharField(max_length=50)
    delboy_email=models.CharField(max_length=50)
    delboy_contact=models.CharField(max_length=50)
    delboy_address=models.CharField(max_length=150)
    delboy_photo=models.FileField(upload_to="Assets/ShopDocs/")
    delboy_proof=models.FileField(upload_to="Assets/ShopDocs/")
    delboy_password=models.CharField(max_length=50)
    delboy_status=models.IntegerField(default=0)
    place = models.ForeignKey(tbl_place,on_delete=models.CASCADE)
