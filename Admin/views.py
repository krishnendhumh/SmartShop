from django.shortcuts import render,redirect
from Admin.models import*
from Guest.models import*
from User.models import*

# Create your views here.
def District(request):
    districtdata = tbl_district.objects.all()
    if request.method == "POST":
        name = (request.POST.get("txt_district"))
        tbl_district.objects.create(district_name=name)
        # return redirect("Admin:District")
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
    categorydata = tbl_category.objects.all()
    if request.method == "POST":
        name = (request.POST.get("txt_category"))
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
    districtdata=  tbl_district.objects.all()
    placedata = tbl_place.objects.all()
    if request.method == "POST":
        place= request.POST.get("txt_place")
        district = tbl_district.objects.get(id=request.POST.get("sel_district"))
        tbl_place.objects.create(place_name = place,district=district)
        return render(request,"Admin/Place.html",{'msg':"Data Inserted.."})
    else:
        return render(request,"Admin/Place.html",{'placedata':placedata, 'districtdata':districtdata})

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
    categorydata=  tbl_category.objects.all()
    subdata = tbl_subcategory.objects.all()
    if request.method == "POST":
        subcategory= request.POST.get("txt_subcategory")
        category = tbl_category.objects.get(id=request.POST.get("sel_category"))
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
    return render(request,"Admin/Homepage.html")
    
def ShopVerification(request):
     pending = tbl_shop.objects.filter(shop_status=0)
     accepted= tbl_shop.objects.filter(shop_status=1)
     rejected = tbl_shop.objects.filter(shop_status=2)
     return render(request,"Admin/ShopVerification.html" ,{'pending':pending,'accepted':accepted,'rejected':rejected})

def accept(request,aid):
    accept= tbl_shop.objects.get(id=aid)
    accept.shop_status=1
    accept.save()
    return render(request,"Admin/ShopVerification.html",{'msg':'Accepted'})
 
def reject(request,rid):
    reject= tbl_shop.objects.get(id=rid)
    reject.shop_status=2
    reject.save()
    return render(request,"Admin/ShopVerification.html",{'msg':' Rejected'})

def Brand(request):
    branddata = tbl_brand.objects.all()
    if request.method == "POST":
        name = (request.POST.get("txt_brand"))
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
   

