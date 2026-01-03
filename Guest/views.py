from django.shortcuts import render,redirect
from Guest.models import*
from Admin.models import*
# Create your views here.
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
        
        tbl_user.objects.create(user_name=name,user_email=email,user_contact=contact,user_address=address,user_photo=photo,user_password=password,place=place)
        
        return render(request,"Guest/UserRegistration.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Guest/UserRegistration.html",{ 'districtdata':districtdata})

def Ajaxplace(request):
    place=tbl_place.objects.filter(district=request.GET.get('districtId'))
    return render(request,"Guest/Ajaxplace.html",{'data':place})



def Login(request):
    if request.method == "POST":
    
        email=request.POST.get("txt_email")
        password=request.POST.get("txt_password")

        usercount = tbl_user.objects.filter(user_email=email,user_password=password).count()
        admincount = tbl_admin.objects.filter(admin_email=email,admin_password=password).count()
        shopcount = tbl_shop.objects.filter(shop_email=email,shop_password=password).count()
        dboycount = tbl_deliveryboy.objects.filter(delboy_email=email,delboy_password=password).count()
        if usercount > 0:
            user = tbl_user.objects.get(user_email=email,user_password=password)
            request.session['uid'] = user.id
            return redirect("User:Homepage")
        
        elif admincount > 0:
            admin = tbl_admin.objects.get(admin_email=email,admin_password=password)
            request.session['aid'] = admin.id
            return redirect("Admin:Homepage")
        
        elif shopcount > 0:
            shop= tbl_shop.objects.get(shop_email=email,shop_password=password)
            request.session['sid'] = shop.id
            return redirect("Shop:Homepage")
        
        elif dboycount > 0:
            dboy= tbl_deliveryboy.objects.get(delboy_email=email,delboy_password=password)
            request.session['did'] = dboy.id
            return redirect("DeliveryBoy:Homepage")
        else:
            return render(request,"Guest/Login.html",{"msg":"Invalid Email or Password"})
    else:
        return render(request,"Guest/Login.html")
    
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

   
   