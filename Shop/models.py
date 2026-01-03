from django.db import models
from Admin.models import *
from Guest.models import *

# Create your models here.
class tbl_staff(models.Model):
    staff_name=models.CharField(max_length=50)
    staff_email=models.CharField(max_length=50)
    staff_password=models.CharField(max_length=50)

class tbl_product(models.Model):
    product_name=models.CharField(max_length=50)
    product_details=models.CharField(max_length=150)
    product_photo=models.FileField(upload_to="Assets/ProdDocs/")
    product_price=models.CharField(max_length=10)
    subcategory = models.ForeignKey(tbl_subcategory,on_delete=models.CASCADE)
    brand = models.ForeignKey(tbl_brand,on_delete=models.CASCADE)
    shop = models.ForeignKey(tbl_shop,on_delete=models.CASCADE)

class tbl_gallery(models.Model):
     gallery_file=models.FileField(upload_to="Assets/ProdDocs/")
     product = models.ForeignKey(tbl_product,on_delete=models.CASCADE)

class tbl_stock(models.Model):
     stock_quantity=models.FileField(upload_to="Assets/ProdDocs/")
     stock_date=models.DateField(auto_now_add=True)
     product = models.ForeignKey(tbl_product,on_delete=models.CASCADE)



