from django.shortcuts import render,redirect
from Guest.models import*
from Shop.models import*
from User.models import*
from django.db.models import Sum
# Create your views here.
def Homepage(request):
    return render(request,"User/Homepage.html")

def MyProfile(request):
    userdata = tbl_user.objects.get(id=request.session['uid'])
    return render(request,"User/MyProfile.html",{'user':userdata})

def EditProfile(request):
    userdata = tbl_user.objects.get(id=request.session['uid'])
    if request.method == "POST":
        name=request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        
        userdata.user_name = name
        userdata.user_email= email
        userdata.user_contact= contact
        userdata.user_address= address
        userdata.save()
    
        return render(request,"User/EditProfile.html",{'msg':"Data Updated.."})
    else:
        return render(request,"User/EditProfile.html",{'user':userdata})

def ChangePass(request):
    userdata = tbl_user.objects.get(id=request.session['uid'])
    dbpass=userdata.user_password
    if request.method == "POST":
        password=request.POST.get("txt_password")
        newpassword=request.POST.get("txt_newpassword")
        repassword=request.POST.get("txt_repassword")
        if dbpass==password:
            if newpassword==repassword:
                userdata.user_password=newpassword
                userdata.save()
                return render(request,'User/ChangePass.html',{'msg':"password changed..."})
            else:
                return render(request,'User/ChangePass.html',{'msg':"password does not match..."}) 
        else:
            return render(request,'User/ChangePass.html',{'msg':"invalid old password"})  
    else:
       
        return render(request,"User/ChangePass.html")

def Viewproduct(request):
    productdata=tbl_product.objects.all()
    categorydata =  tbl_category.objects.all()
    branddata=tbl_brand.objects.all()
    return render(request,"User/Viewproduct.html",{'product':productdata,'categorydata':categorydata,'branddata':branddata})

def Viewmore(request,id):
    productdata = tbl_product.objects.get(id=id)
    gallerydata=tbl_gallery.objects.filter(product=id)
    return render(request,"User/Viewmore.html",{'product':productdata,'gallery':gallerydata})

def Addcart(request):
    return render(request,"User/Addcart.html")

def AjaxSearch(request):
    name = request.GET.get("name")
    category = request.GET.get("categoryId")
    subcategory = request.GET.get("subcategoryId")
    brand = request.GET.get("brandId")

    productdata = tbl_product.objects.all()

    if name:
        productdata = productdata.filter(product_name__icontains=name)

    if category:
        productdata = productdata.filter(subcategory__category=category)

    if subcategory:
        productdata = productdata.filter(subcategory=subcategory)

    if brand:
        productdata = productdata.filter(brand=brand)

    return render(request, "User/AjaxSearch.html", {'productdata': productdata})

def Wishlist(request,id):
    productdata = tbl_product.objects.get(id=id)
    productID=tbl_product.objects.get(id=id)
    userID=tbl_user.objects.get(id=request.session['uid'])
    wishlistcount=tbl_wishlist.objects.filter(user=userID,product=productID).count()
    if wishlistcount > 0:
        tbl_wishlist.objects.get(user=userID,product=productID).delete()
        return render(request,"User/Viewproduct.html",{'msg':"removed.."})
    else:
        tbl_wishlist.objects.create(product=productID,user=userID)
        return render(request, "User/Viewproduct.html", {'msg':"Wishlist added.."})
    
def Wishlists(request):
    wishlistdata=tbl_wishlist.objects.filter(user=request.session['uid'])
    return render(request, "User/Wishlist.html",{'wishlist':wishlistdata})


def Complaint(request):
    if request.method == "POST":
        title = request.POST.get("txt_title")
        content = request.POST.get("txt_content")

        tbl_complaint.objects.create(
            com_title=title,
            com_content=content,
            user_id=request.session['uid'] 
        )

        return render(request, "User/Complaint.html")  
    complaints = tbl_complaint.objects.filter(
        user_id=request.session['uid']
    )

    return render(request, "User/Complaint.html", {"complaints": complaints})


def delcomplaint(request,id):
    tbl_complaint.objects.filter(id=id).delete()
    return render(request, "User/Complaint.html")

def Feedback(request):
    if request.method == "POST":
        
        content = request.POST.get("txt_content")

        tbl_feedback.objects.create(
            
            feed_content=content,
            user_id=request.session['uid'] 
        )

        return render(request, "User/Feedback.html",{'msg':"Feedback added.."})  
    feedback = tbl_feedback.objects.filter(
        user_id=request.session['uid']
    )

    return render(request, "User/Feedback.html",{'feedback':feedback})

def delfeedback(request,id):
    tbl_feedback.objects.filter(id=id).delete()
    return render(request, "User/Feedback.html")

def Addcart(request,id):
    productID=tbl_product.objects.get(id=id)
    userID=tbl_user.objects.get(id=request.session['uid'])
    bookingcount = tbl_booking.objects.filter(booking_status=0,user=userID).count()
    if bookingcount > 0 :
        bookingdata = tbl_booking.objects.get(booking_status=0,user=userID)
        cartcount = tbl_cart.objects.filter(cart_status=0,booking=bookingdata,product=productID).count()
        if cartcount > 0:
            return render(request,"User/Viewproduct.html",{'msg':"Already Added to Cart"})
        else:
            tbl_cart.objects.create(booking=bookingdata,product=productID)
            return render(request, "User/Viewproduct.html",{'msg':"Added to Cart"})
            
    else:
        bookingdata=tbl_booking.objects.create(user=userID)
        tbl_cart.objects.create(booking=bookingdata,product=productID)
        return render(request, "User/Viewproduct.html",{'msg':'Added to Cart'})
    
def Mycart(request):
        if request.method=="POST":
            bookingdata=tbl_booking.objects.get(id=request.session["bookingid"])
            bookingdata.booking_amount=request.POST.get("carttotalamt")
            bookingdata.booking_status=1
            bookingdata.save()
            cart = tbl_cart.objects.filter(booking=bookingdata)
            for i in cart:
                i.cart_status = 1
                i.save()
            return redirect("User:payment")
        else:
            bookcount = tbl_booking.objects.filter(user=request.session["uid"],booking_status=0).count()
            if bookcount > 0:
                book = tbl_booking.objects.get(user=request.session["uid"],booking_status=0)
                request.session["bookingid"] = book.id
                cart = tbl_cart.objects.filter(booking=book)
                for i in cart:
                    total_stock = tbl_stock.objects.filter(product=i.product.id).aggregate(total=Sum('stock_quantity'))['total']
                    total_cart = tbl_cart.objects.filter(product=i.product.id, cart_status=1).aggregate(total=Sum('cart_qty'))['total']
                    # print(total_stock)
                    # print(total_cart)
                    if total_stock is None:
                        total_stock = 0
                    if total_cart is None:
                        total_cart = 0
                    total =  total_stock - total_cart
                    i.total_stock = total
                return render(request,"User/MyCart.html",{'cartdata':cart})
            else:
                return render(request,"User/MyCart.html")
   
        

def DelCart(request,did):
   tbl_cart.objects.get(id=did).delete()
   return redirect("User:MyCart")

def CartQty(request):
   qty=request.GET.get('QTY')
   cartid=request.GET.get('ALT')
   cartdata=tbl_cart.objects.get(id=cartid)
   cartdata.cart_qty=qty
   cartdata.save()
   return redirect("User:MyCart")  

def payment(request): 
    bookingdata=tbl_booking.objects.get(id=request.session["bookingid"])
    if request.method=="POST":
        bookingdata.booking_status=2
        bookingdata.save()
        cartdata = tbl_cart.objects.filter(booking=bookingdata)
        for i in cartdata:
            i.cart_status = 2
            i.save()
        return render(request,"User/payment.html",{'msg':'Payment in process '})
    else:
        return render(request,"User/payment.html",{'bookingdata':bookingdata})
    
def MyBooking(request):
    bookingdata=tbl_booking.objects.filter(user=request.session['uid'])
    return render(request,"User/MyBooking.html",{'bookingdata':bookingdata})
 


            
            













