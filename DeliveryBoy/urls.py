from django.urls import path
from DeliveryBoy import views
app_name ="DeliveryBoy"


urlpatterns = [
    path('Homepage/',views.Homepage,name="Homepage"),
    path('Myprofile/',views.MyProfile,name="Myprofile"),
    path('Editprofile/',views.EditProfile,name="Editprofile"),
    path('ChangePass/',views.ChangePass,name="ChangePass"),
]