from django.db import models
from Guest.models import *
from Shop.models import *
# Create your models here.

class tbl_wishlist(models.Model):
    product = models.ForeignKey(tbl_product,on_delete=models.CASCADE)
    user = models.ForeignKey(tbl_user,on_delete=models.CASCADE)

class tbl_complaint(models.Model):
    com_title = models.CharField(max_length=200)
    com_content = models.TextField()
    com_date = models.DateField(auto_now_add=True)
    com_status=models.IntegerField(default=0)
    com_reply = models.TextField( null=True)
    user = models.ForeignKey(tbl_user,on_delete=models.CASCADE)

class tbl_feedback(models.Model):
    feed_content= models.TextField()
    feed_date= models.DateField(auto_now_add=True)
    user = models.ForeignKey(tbl_user,on_delete=models.CASCADE)

class tbl_booking(models.Model):
    booking_status= models.IntegerField(default=0)
    booking_amount = models.FloatField(null=True)
    booking_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(tbl_user,on_delete=models.CASCADE)

class tbl_cart(models.Model):
    cart_qty = models.IntegerField(default=1)
    cart_status = models.IntegerField(default=0)
    product = models.ForeignKey(tbl_product,on_delete=models.CASCADE)
    booking = models.ForeignKey(tbl_booking,on_delete=models.CASCADE)
    pack_date= models.DateField(null=True)
    ship_date = models.DateField(null=True)
    outdel_date = models.DateField(null=True)
    del_date = models.DateField(null=True)



