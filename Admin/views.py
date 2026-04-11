from django.shortcuts import render,redirect
from Admin.models import*
from Guest.models import*
from User.models import*
from Shop.models import*
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def logout(request):
    del request.session['aid']
    return redirect("Guest:Login")

def District(request):
    if "aid" not in request.session:    
        return redirect("Guest:Login")
    else:
        districtdata = tbl_district.objects.all().order_by('district_name')
        if request.method == "POST":
            name = (request.POST.get("txt_district"))
            districtcount=tbl_district.objects.filter(district_name=name).count()
            if districtcount > 0:
                return render(request,"Admin/District.html",{'msg':"Already Inserted.."})
            else:
                tbl_district.objects.create(district_name=name)
            
            return render(request,"Admin/District.html",{'msg':"Data Inserted.."})
        else:
            return render(request,"Admin/District.html",{'districtdata':districtdata})

def deldistrict(request,did):
    tbl_district.objects.get(id=did).delete()
    return render(request,"Admin/District.html",{'msg':"Data Deleted.."})

def editdistrict(request,eid):
    editdata = tbl_district.objects.get(id=eid)
    districtdata = tbl_district.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_district")
        editdata.district_name = name
        editdata.save()
        return render(request,"Admin/District.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/District.html",{'editdata':editdata,'districtdata':districtdata})
   
def AdminRegistration(request):
    admindata = tbl_admin.objects.all()
    if request.method == "POST":
        name = (request.POST.get("txt_name"))
        email=(request.POST.get("txt_mail"))
        password=(request.POST.get("txt_password"))
        tbl_admin.objects.create(admin_name=name,admin_email=email,admin_password=password)
       
        return render(request,"Admin/AdminRegistration.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Admin/AdminRegistration.html",{'admindata':admindata})

def deladmindata(request,did):
    tbl_admin.objects.get(id=did).delete()
    return render(request,"Admin/AdminRegistration.html",{'msg':"Data Deleted.."})

def editadmindata(request,eid):
    editdata = tbl_admin.objects.get(id=eid)
    admindata = tbl_admin.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_name")
        editdata.admin_name = name
        email=request.POST.get("txt_mail")
        editdata.admin_email = email
        password=request.POST.get("txt_password")
        editdata.save()
        return render(request,"Admin/AdminRegistration.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/AdminRegistration.html",{'editdata':editdata,'admindata':admindata})
   
def Category(request):
    if "aid" not in request.session:    
        return redirect("Guest:Login")
    else:
        categorydata = tbl_category.objects.all()
        
        if request.method == "POST":
            name = (request.POST.get("txt_category"))
            catcount=tbl_category.objects.filter(category_name=name).count()
            if catcount > 0:
                return render(request,"Admin/Category.html",{'msg':"Already Inserted.."})
            else:
                tbl_category.objects.create(category_name=name)

            return render(request,"Admin/Category.html",{'msg':"Data Inserted.."})
        else:
            return render(request,"Admin/Category.html",{'categorydata':categorydata})

def delcategory(request,did):
    tbl_category.objects.get(id=did).delete()
    return render(request,"Admin/Category.html",{'msg':"Data Deleted.."})

def editcategory(request,eid):
    editdata = tbl_category.objects.get(id=eid)
    categorydata = tbl_category.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_category")
        editdata.category_name = name
        editdata.save()
        return render(request,"Admin/Category.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/Category.html",{'editdata':editdata,'categorydata':categorydata})
   
    
def Place(request):
    districtdata = tbl_district.objects.all()
    # Order first by District Name, then alphabetically by Place Name
    placedata = tbl_place.objects.all().order_by('district__district_name', 'place_name')

    if request.method == "POST":
        place = request.POST.get("txt_place")
        district_id = request.POST.get("sel_district")
        district = tbl_district.objects.get(id=district_id)
        
        # Check if the place already exists in that SPECIFIC district
        placecount = tbl_place.objects.filter(place_name=place, district=district).count()

        if placecount > 0:
            return render(request, "Admin/Place.html", {
                'msg': "Already Inserted..", 
                'placedata': placedata, 
                'districtdata': districtdata
            })
        else:
            tbl_place.objects.create(place_name=place, district=district)
            return render(request, "Admin/Place.html", {
                'msg': "Data Inserted..", 
                'placedata': placedata, 
                'districtdata': districtdata
            })
    else:
        return render(request, "Admin/Place.html", {
            'placedata': placedata, 
            'districtdata': districtdata
        })
def delplace(request,did):
    tbl_place.objects.get(id=did).delete()
    return render(request,"Admin/Place.html",{'msg':"Data Deleted.."})

def editplace(request,eid):
    editdata = tbl_place.objects.get(id=eid)
    placedata = tbl_place.objects.all()
    districtdata=tbl_district.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_place")
        district=tbl_district.objects.get(id=request.POST.get("sel_district"))
        editdata.place_name = name
        editdata.district = district
        editdata.save()
        return render(request,"Admin/Place.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/Place.html",{'editdata':editdata,'placedata':placedata,'districtdata':districtdata})
   
    
def SubCategory(request):
    if "aid" not in request.session:    
        return redirect("Guest:Login")
    else:
        categorydata=  tbl_category.objects.all()
        # This orders first by Category Name, then alphabetically by Subcategory Name
        subdata = tbl_subcategory.objects.all().order_by('category__category_name', 'subcategory_name')
        if request.method == "POST":
            subcategory= request.POST.get("txt_subcategory")
            category = tbl_category.objects.get(id=request.POST.get("sel_category"))
            subcatcount=tbl_subcategory.objects.filter(subcategory_name=subcategory).count()
            if subcatcount > 0:
                return render(request,"Admin/SubCategory.html",{'msg':"Already Inserted.."})
            else:
                tbl_subcategory.objects.create(subcategory_name = subcategory,category=category)
            return render(request,"Admin/SubCategory.html",{'msg':"Data Inserted.."})
        else:
            return render(request,"Admin/SubCategory.html",{'subdata':subdata, 'categorydata':categorydata})

def delsub(request,did):
    tbl_subcategory.objects.get(id=did).delete()
    return render(request,"Admin/SubCategory.html",{'msg':"Data Deleted.."})

def editsub(request,eid):
    editdata = tbl_subcategory.objects.get(id=eid)
    subdata = tbl_subcategory.objects.all()
    categorydata=tbl_category.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_subcategory")
        category=tbl_category.objects.get(id=request.POST.get("sel_category"))
        editdata.subcategory_name = name
        editdata.category = category
        editdata.save()
        return render(request,"Admin/SubCategory.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/SubCategory.html",{'editdata':editdata,'subdata':subdata,'categorydata':categorydata})

def Homepage(request):
    user_count = tbl_user.objects.count()
    shop_count = tbl_shop.objects.count()
    product_count = tbl_product.objects.count()
    booking_count = tbl_booking.objects.count()

    context = {
        "user_count": user_count,
        "shop_count": shop_count,
        "product_count": product_count,
        "booking_count": booking_count
    }

    return render(request,"Admin/HomePage.html",context)
    
from django.core.mail import send_mail
from django.conf import settings

def ShopVerification(request):
    pending = tbl_shop.objects.filter(shop_status=0)
    accepted = tbl_shop.objects.filter(shop_status=1)
    rejected = tbl_shop.objects.filter(shop_status=2)
    return render(
        request,
        "Admin/ShopVerification.html",
        {'pending': pending, 'accepted': accepted, 'rejected': rejected}
    )


def accept(request, aid):
    shop = tbl_shop.objects.get(id=aid)
    shop.shop_status = 1
    shop.save()

    subject = "Shop Verification Approved 🎉"
    message = f"""
Hello {shop.shop_name},

Congratulations! 🎉

Your shop has been successfully verified and approved by our admin team.
You can now log in and start managing your products and orders.

Welcome aboard!
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [shop.shop_email],
    )

    return redirect("Admin:ShopVerification")


def reject(request, rid):
    shop = tbl_shop.objects.get(id=rid)
    shop.shop_status = 2
    shop.save()

    subject = "Shop Verification Rejected ❌"
    message = f"""
Hello {shop.shop_name},

We regret to inform you that your shop verification request has been rejected.

This may be due to incomplete or incorrect information.
Please review your details and contact support for further assistance.

Thank you for your interest.
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [shop.shop_email],
    )

    return redirect("Admin:ShopVerification")

def Brand(request):
    if "aid" not in request.session:    
        return redirect("Guest:Login")
    else:
        # Orders brands alphabetically A-Z
        branddata = tbl_brand.objects.all().order_by('brand_name')
        if request.method == "POST":
            name = (request.POST.get("txt_brand"))
            brandcount=tbl_brand.objects.filter(brand_name=name).count()
            if brandcount > 0:
                return render(request,"Admin/Brand.html",{'msg':"Already Inserted.."})
            else:
                tbl_brand.objects.create(brand_name=name)
        
            return render(request,"Admin/Brand.html",{'msg':"Data Inserted.."})
        else:
            return render(request,"Admin/Brand.html",{'branddata':branddata})

def delbrand(request,did):
        tbl_brand.objects.get(id=did).delete()
        return render(request,"Admin/Brand.html",{'msg':"Data Deleted.."})

def editbrand(request,eid):
    editdata = tbl_brand.objects.get(id=eid)
    branddata = tbl_brand.objects.all()
    if request.method == "POST":
        name=request.POST.get("txt_brand")
        editdata.brand_name = name
        editdata.save()
        return render(request,"Admin/Brand.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Admin/Brand.html",{'editdata':editdata,'branddata':branddata})
    

def Viewcomplaint(request):
    complaints = tbl_complaint.objects.all().order_by("-com_date")
    return render(request, "Admin/Viewcomplaint.html", {"complaints": complaints})


def replycomplaint(request, id):
    complaint = tbl_complaint.objects.get(id=id)

    if request.method == "POST":
        reply = request.POST.get("txt_reply")
        complaint.com_reply = reply
        complaint.save()
        return redirect("Admin:Viewcomplaint")

    return render(
        request,
        "Admin/ReplyComplaint.html",
        {"complaint": complaint}
    )

def Viewfeedback(request):
    feedback = tbl_feedback.objects.all().order_by("-feed_date")
    return render(request, "Admin/Viewfeedback.html", {"feedback": feedback})

def SalesReport(request):
    # 1. Initialize variables with default values
    from_date = request.POST.get("from_date")
    to_date = request.POST.get("to_date")
    
    # 2. Start with a base queryset (All bookings)
    booking_qs = tbl_booking.objects.all()

    # 3. Apply Filter ONLY if POST and dates are provided
    if request.method == "POST" and from_date and to_date:
        booking_qs = booking_qs.filter(booking_date__range=[from_date, to_date])

    # 4. Filter Cart/Feedback based on the filtered Bookings
    # This ensures your summary cards (Total Sales, Cancels) match the date range
    total_sales = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=6).count()
    cancel_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=7).count()
    return_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=9).count()
    refund_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=10).count()
    
    # Assuming feedback is linked to booking or product; if not, you might need a date field in tbl_feedback
    feedback_count = tbl_feedback.objects.all().count() 

    context = {
        "bookingdata": booking_qs,
        "total_sales": total_sales,
        "cancel_count": cancel_count,
        "return_count": return_count,
        "refund_count": refund_count,
        "feedback_count": feedback_count,
        "from_date": from_date, # Pass this back to keep the input filled
        "to_date": to_date      # Pass this back to keep the input filled
    }

    return render(request, "Admin/SalesReport.html", context)
def UserList(request):
    userdata=tbl_user.objects.all()
    return render(request, "Admin/UserList.html", {"userdata": userdata})



def blockuser(request, id):
    user = tbl_user.objects.get(id=id)
    user.user_status = 0
    user.save()

    subject = "Account Blocked Notification ⚠️"
    message = f"""
Hello {user.user_name},

Your account has been temporarily blocked by the admin.

Possible reasons may include:
- Violation of platform policies
- Suspicious activities
- Multiple failed verification attempts

If you believe this is a mistake, please contact our support team.

Thank you,
Admin Team
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )

    return redirect("Admin:UserList")

def unblockuser(request, id):
    user = tbl_user.objects.get(id=id)
    user.user_status = 1
    user.save()

    send_mail(
        "Account Reactivated ✅",
        f"""
Hello {user.user_name},

Good news! 🎉
Your account has been reactivated. You can now log in and continue using our services.

Welcome back!
""",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )

    return redirect("Admin:UserList")

from datetime import date

def ApproveCancel(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    cart.cart_status = 8  
    cart.approve_date = date.today()
    cart.save()
    return redirect("Admin:ViewRequests")


def ApproveReturn(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    cart.cart_status = 10  
    cart.approve_date = date.today()
    cart.save()
    return redirect("Admin:ViewRequests")

from datetime import timedelta

def ProcessRefund(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    if cart.cart_status in [8, 10]:
        if date.today() >= cart.approve_date + timedelta(days=2):
            cart.cart_status = 12  # Refunded
            cart.save()

            send_mail(
                "Refund Processed",
                f"Hello {user.user_name},\n\nYour refund has been processed successfully.",
                settings.EMAIL_HOST_USER,
                [user.user_email],
            )

    return redirect("Admin:RefundList")

def AdminHome(request):

    user_count = tbl_user.objects.count()
    shop_count = tbl_shop.objects.count()
    product_count = tbl_product.objects.count()
    booking_count = tbl_booking.objects.count()

    cancel_count = tbl_cart.objects.filter(cart_status=7).count()
    return_count = tbl_cart.objects.filter(cart_status=9).count()

    context = {
        "user_count": user_count,
        "shop_count": shop_count,
        "product_count": product_count,
        "booking_count": booking_count,
        "cancel_count": cancel_count,
        "return_count": return_count
    }

    return render(request,"Admin/HomePage.html",context)








   

