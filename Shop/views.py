from django.shortcuts import render,redirect
from Guest.models import*
from Shop.models import*
from User.models import*
from datetime import date
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

# Create your views here.

def logout(request):
    del request.session['aid']
    return redirect("Guest:Login")

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
   
    for product in productdata:
        total_stock = tbl_stock.objects.filter(
            product=product
        ).aggregate(total=Sum('stock_quantity'))['total'] or 0

        total_cart = tbl_cart.objects.filter(
            product=product,
            cart_status=1
        ).aggregate(total=Sum('cart_qty'))['total'] or 0

        product.total_stock = max(total_stock - total_cart, 0)
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
    bookingdata=tbl_booking.objects.all()
    return render(request,"Shop/ViewBooking.html",{'bookingdata':bookingdata})

def BookingAction(request, cid, status):
    cart = tbl_cart.objects.get(id=cid)
    booking = cart.booking
    user = booking.user
    email = user.user_email

    subject = "Order Status Update"

    # PACKED
    if status == 3:
        cart.cart_status = 3
        cart.pack_date = date.today()

        message = f"""
Hello {user.user_name},

📦 Your order has been packed successfully.

It will be shipped shortly.

Thank you for shopping with us.
"""

    # SHIPPED
    elif status == 4:
        cart.cart_status = 4
        cart.ship_date = date.today()

        message = f"""
Hello {user.user_name},
🚚 Good news!
Your order has been shipped.

It will reach you soon.

Thank you for shopping with us.
"""

    # OUT FOR DELIVERY
    elif status == 5:
        cart.cart_status = 5
        cart.outdel_date = date.today()

        message = f"""
Hello {user.user_name},

🚚 Your order is out for delivery today.

Please keep your phone available.

Thank you for choosing us.
"""

    # DELIVERED
    elif status == 6:
        cart.cart_status = 6
        cart.del_date = date.today()

        message = f"""
Hello {user.user_name},

🎉 Your order has been delivered successfully!

We hope you enjoy your purchase.
Thank you for shopping with us.
"""

    # SAVE CART
    cart.save()

    # SEND MAIL
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=True
    )

    return redirect("Shop:ViewBooking")

def SalesReport(request):
    bookingdata = None
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        bookingdata = tbl_booking.objects.filter(
            booking_date__range=[from_date, to_date]
        )

    return render(request, "Shop/SalesReport.html", {
        'bookingdata': bookingdata
    })
from datetime import date
def ViewRequests(request):
    cancel_requests = tbl_cart.objects.filter(cart_status=7)
    return_requests = tbl_cart.objects.filter(cart_status=9)

    return render(request, "Shop/ViewRequests.html", {
        "cancel_requests": cancel_requests,
        "return_requests": return_requests
    })


def ApproveCancel(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 8  # Cancel Approved
    cart.save()
    messages.success(request, "✅ Cancel request approved successfully.")

    send_mail(
        "Cancel Approved",
        f"Hello {user.user_name},\n\nYour cancellation request has been approved.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )

    return redirect("Shop:ViewRequests")

def ApproveReturn(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 10  # Return Approved
    cart.save()
    

    send_mail(
        "Return Approved",
        f"Hello {user.user_name},\n\nYour return request has been approved.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )
    messages.success(request, "✅ Return request approved successfully.")

    return redirect("Shop:ViewRequests")

    return redirect("Shop:RefundList")
def RejectRequest(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 11  # Rejected
    cart.reject_reason = "Rejected by shop"
    cart.save()

    send_mail(
        "Request Rejected",
        f"Hello {user.user_name},\n\nYour request has been rejected by the shop.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )
    messages.error(request, "❌ Request rejected.")
    return redirect("Shop:ViewRequests")







