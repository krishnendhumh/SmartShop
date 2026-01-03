from django.shortcuts import render,redirect
from Guest.models import*
from Shop.models import*
from User.models import*
from datetime import date

# Create your views here.
def Homepage(request):
    return render(request,"Shop/Homepage.html")

def MyProfile(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    return render(request,"Shop/MyProfile.html",{'shop':shopdata})

def EditProfile(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    if request.method == "POST":
        name=request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        
        shopdata.shop_name = name
        shopdata.shop_email= email
        shopdata.shop_contact= contact
        shopdata.shop_address= address
        shopdata.save()
    
        return render(request,"Shop/EditProfile.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Shop/EditProfile.html",{'shop':shopdata})

def ChangePass(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    dbpass=shopdata.shop_password
    if request.method == "POST":
        password=request.POST.get("txt_password")
        newpassword=request.POST.get("txt_newpassword")
        repassword=request.POST.get("txt_repassword")
        if dbpass==password:
            if newpassword==repassword:
                shopdata.shop_password=newpassword
                shopdata.save()
                return render(request,'Shop/ChangePass.html',{'msg':"password changed..."})
            else:
                return render(request,'Shop/ChangePass.html',{'msg':"password does not match..."}) 
        else:
            return render(request,'Shop/ChangePass.html',{'msg':"invalid old password"})  
    else:
       
        return render(request,"Shop/ChangePass.html")
    
def AddStaff(request):
    staffdata=tbl_staff.objects.all()
    if request.method == "POST":
        name= request.POST.get("txt_name")
        email= request.POST.get("txt_email")
        password=request.POST.get("txt_password")
        tbl_staff.objects.create(staff_name=name, staff_email=email,staff_password=password)
        return render(request,"Shop/AddStaff.html",{'msg':"Data inserted.."})
    else:
        return render(request,"Shop/AddStaff.html",{'staffdata':staffdata})
    
def Product(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    categorydata =  tbl_category.objects.all()
    branddata=tbl_brand.objects.all()
    productdata=tbl_product.objects.filter(shop=shopdata)
    if request.method == "POST":
        name=request.POST.get("txt_name")
        details=request.POST.get("txt_details")
        photo=request.FILES.get("file_photo")
        price=request.POST.get("txt_price")
        subcategory= tbl_subcategory.objects.get(id=request.POST.get("sel_subcategory"))
        brand= tbl_brand.objects.get(id=request.POST.get("sel_brand"))
        tbl_product.objects.create(product_name=name, product_details=details,product_photo=photo,product_price=price,shop=shopdata,brand=brand,subcategory=subcategory)
        return render(request,"Shop/Product.html",{'msg':"Data inserted.."})
    else:
        return render(request,"Shop/Product.html",{'categorydata':categorydata,'branddata':branddata,'product':productdata})

def Ajaxsubcategory(request):
    subcategory=tbl_subcategory.objects.filter(category=request.GET.get('categoryId'))
    return render(request,"Shop/Ajaxsubcategory.html",{'data':subcategory})

def Gallery(request,id):
    gallerydata=tbl_gallery.objects.filter(product=id)
    productID=tbl_product.objects.get(id=id)
    if request.method == "POST":
        photo=request.FILES.get("file_photo")
        tbl_gallery.objects.create(gallery_file=photo,product=productID)
        return render(request,"Shop/Gallery.html",{'msg':"Image inserted.."})
    else:
        return render(request,"Shop/Gallery.html",{'gallery':gallerydata})

def Stock(request,id):
    stock=tbl_stock.objects.filter(product=id)
    productID=tbl_product.objects.get(id=id)
    if request.method == "POST":
        stock=request.POST.get("num_stock")
        tbl_stock.objects.create(stock_quantity=stock,product=productID)
        return render(request,"Shop/Stock.html",{'msg':"Stock inserted.."})
    else:
       
        return render(request,"Shop/Stock.html",{'stock':stock})

def delstock(request,did):
    
    tbl_stock.objects.get(id=did).delete()
    return render(request,"Shop/Stock.html",{'msg':"Data Deleted.."})

def delgallery(request,did):
    
    tbl_gallery.objects.get(id=did).delete()
    return render(request,"Shop/Gallery.html",{'msg':"Data Deleted.."})

def ViewBooking(request):
    bookingdata=tbl_booking.objects.filter(user=request.session['uid'])
    return render(request,"Shop/ViewBooking.html",{'bookingdata':bookingdata})

def BookingAction(request,cid,status):
    cart = tbl_cart.objects.get(id=cid)
    cart.cart_status = status
    if status == 3:
        cart.pack_date= date.today()
    elif status == 4:
        cart.ship_date = date.today()
    elif status == 5:
        cart.outdel_date = date.today()
    elif status == 6:
        cart.del_date = date.today()
    
        
    cart.save()        
    return redirect("Shop:ViewBooking")



