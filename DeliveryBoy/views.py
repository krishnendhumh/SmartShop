from django.shortcuts import render
from Guest.models import*

# Create your views here.
def Homepage(request):
    return render(request,"DeliveryBoy/Homepage.html")

def MyProfile(request):
    dboydata = tbl_deliveryboy.objects.get(id=request.session['did'])
    return render(request,"DeliveryBoy/Myprofile.html",{'dboy':dboydata})

def EditProfile(request):
    dboydata = tbl_deliveryboy.objects.get(id=request.session['did'])
    if request.method == "POST":
        name=request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        
        dboydata.delboy_name = name
        dboydata.delboy_email= email
        dboydata.delboy_contact= contact
        dboydata.delboy_address= address
        dboydata.save()
    
        return render(request,"DeliveryBoy/Editprofile.html",{'msg':"Data Updated.."})
    else:
        return render(request,"DeliveryBoy/Editprofile.html",{'dboy':dboydata})

def ChangePass(request):
    dboydata = tbl_deliveryboy.objects.get(id=request.session['did'])
    dbpass=dboydata.delboy_password
    if request.method == "POST":
        password=request.POST.get("txt_password")
        newpassword=request.POST.get("txt_newpassword")
        repassword=request.POST.get("txt_repassword")
        if dbpass==password:
            if newpassword==repassword:
                dboydata.delboy_password=newpassword
                dboydata.save()
                return render(request,'DeliveryBoy/ChangePass.html',{'msg':"password changed..."})
            else:
                return render(request,'DeliveryBoy/ChangePass.html',{'msg':"password does not match..."}) 
        else:
            return render(request,'DeliveryBoy/ChangePass.html',{'msg':"invalid old password"})  
    else:
       
        return render(request,"DeliveryBoy/ChangePass.html")