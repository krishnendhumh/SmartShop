from django.shortcuts import render,redirect
from Guest.models import*
from Admin.models import*
from Shop.models import*
from django.core.mail import send_mail
from django.conf import settings
import random, datetime
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
def index(request):
    productdata = tbl_product.objects.all()[:4]  # Limit to 4 for index page
    return render(request,"Guest/index.html", {'products': productdata})

def UserRegistration(request):
    districtdata =  tbl_district.objects.all()
    if request.method == "POST":
        name= request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        photo=request.FILES.get("file_photo")
        password=request.POST.get("txt_password")
        place= tbl_place.objects.get(id=request.POST.get("sel_place"))
        usercount=tbl_user.objects.filter(user_email=email).count()
        if usercount > 0:
            return render(request,"Admin/UserRegistration.html",{'msg':"Email Already Inserted.."})
        else:
            tbl_user.objects.create(user_name=name,user_email=email,user_contact=contact,user_address=address,user_photo=photo,user_password=password,place=place)
        
        return render(request,"Guest/UserRegistration.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Guest/UserRegistration.html",{ 'districtdata':districtdata})

def Ajaxplace(request):
    place=tbl_place.objects.filter(district=request.GET.get('districtId'))
    return render(request,"Guest/Ajaxplace.html",{'data':place})



def Login(request):
    if request.method == "POST":

        email = request.POST.get("txt_email")
        password = request.POST.get("txt_password")

        usercount = tbl_user.objects.filter(
            user_email=email,
            user_password=password,
            user_status=1
        ).count()

        admincount = tbl_admin.objects.filter(
            admin_email=email,
            admin_password=password
        ).count()

        shopcount = tbl_shop.objects.filter(
            shop_email=email,
            shop_password=password
        ).count()

        dboycount = tbl_deliveryboy.objects.filter(
            delboy_email=email,
            delboy_password=password
        ).count()

        
        if usercount > 0:
            user = tbl_user.objects.get(
                user_email=email,
                user_password=password
            )
            request.session['uid'] = user.id
            return redirect("User:Homepage")

        
        elif admincount > 0:
            admin = tbl_admin.objects.get(
                admin_email=email,
                admin_password=password
            )
            request.session['aid'] = admin.id
            return redirect("Admin:Homepage")

        
        elif shopcount > 0:
            shop = tbl_shop.objects.get(
                shop_email=email,
                shop_password=password
            )

            if shop.shop_status == 0:
                return render(request, "Guest/Login.html", {
                    "msg": "Verification Pending"
                })
            else:
                request.session['sid'] = shop.id
                return redirect("Shop:Homepage")

      
        elif dboycount > 0:
            dboy = tbl_deliveryboy.objects.get(
                delboy_email=email,
                delboy_password=password
            )
            request.session['did'] = dboy.id
            return redirect("DeliveryBoy:Homepage")

        # INVALID LOGIN
        else:
            return render(request, "Guest/Login.html", {
                "msg": "Invalid login or account blocked"
            })

    else:
        return render(request, "Guest/Login.html")

    
def ShopReg(request):
    districtdata =  tbl_district.objects.all()
    if request.method == "POST":
        name= request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact") 
        address=request.POST.get("txt_address")
        photo=request.FILES.get("file_photo")
        proof=request.FILES.get("file_proof")
        password=request.POST.get("txt_password")
        place= tbl_place.objects.get(id=request.POST.get("sel_place"))
        shopcount=tbl_shop.objects.filter(shop_email=email).count()
        if shopcount > 0:
            return render(request,"Admin/ShopReg.html",{'msg':"Email Already Inserted.."})
        else:
        
            tbl_shop.objects.create(shop_name=name,shop_email=email,shop_contact=contact,shop_address=address,shop_photo=photo,shop_proof=proof,shop_password=password,place=place)
        
        return render(request,"Guest/ShopReg.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Guest/ShopReg.html",{ 'districtdata':districtdata})

        
def DeliveryBoy(request):
    districtdata =  tbl_district.objects.all()
    if request.method == "POST":
        name= request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        photo=request.FILES.get("file_photo")
        proof=request.FILES.get("file_proof")
        password=request.POST.get("txt_password")
        place= tbl_place.objects.get(id=request.POST.get("sel_place"))
        
        tbl_deliveryboy.objects.create(delboy_name=name,delboy_email=email,delboy_contact=contact,delboy_address=address,delboy_photo=photo,delboy_proof=proof,delboy_password=password,place=place)
        
        return render(request,"Guest/DeliveryBoy.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Guest/DeliveryBoy.html",{ 'districtdata':districtdata})



def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get("txt_email")

        user_obj = None
        role = None

        # Check Shop
        user_obj = tbl_shop.objects.filter(shop_email=email).first()
        if user_obj:
            role = "shop"

        # Check User
        if not user_obj:
            user_obj = tbl_user.objects.filter(user_email=email).first()
            if user_obj:
                role = "user"

        if not user_obj:
            return render(request, "Guest/ForgotPassword.html", {
                "msg": "Email not found"
            })

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Store in session (use different keys ❗)
        request.session["reset_otp"] = otp
        request.session["reset_id"] = user_obj.id
        request.session["reset_role"] = role

        # Send Email
        send_mail(
            'Password Reset OTP',
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        return redirect("Guest:otp")

    return render(request, "Guest/ForgotPassword.html")


def otp(request):
    if request.method == "POST":
        inp_otp = request.POST.get("txt_otp")

        session_otp = request.session.get("reset_otp")

        if not session_otp:
            return redirect("Guest:forgotpassword")

        if inp_otp == session_otp:
            return redirect("Guest:newpass")
        else:
            return render(request, "Guest/OTP.html", {
                "msg": "Invalid OTP!"
            })

    return render(request, "Guest/OTP.html")


def newpass(request):
    if request.method == "POST":

        uid = request.session.get("reset_id")
        role = request.session.get("reset_role")

        if not uid or not role:
            return redirect("Guest:forgotpassword")

        new_pass = request.POST.get("txt_newpassword")
        con_pass = request.POST.get("txt_confirmpassword")

        if new_pass != con_pass:
            return render(request, "Guest/NewPassword.html", {
                "msg": "Passwords do not match!"
            })

        # Update Password
        if role == "shop":
            shop = tbl_shop.objects.get(id=uid)
            shop.shop_password = new_pass
            shop.save()

        elif role == "user":
            user = tbl_user.objects.get(id=uid)
            user.user_password = new_pass
            user.save()

        # Clear only reset session (better than flush)
        request.session.pop("reset_id", None)
        request.session.pop("reset_role", None)
        request.session.pop("reset_otp", None)

        return render(request, "Guest/Login.html", {
            "msg": "Password updated successfully!"
        })

    return render(request, "Guest/NewPassword.html")