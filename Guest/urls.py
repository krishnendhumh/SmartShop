from django.urls import path
from Guest import views
app_name ="Guest"


urlpatterns = [
    path('Login/',views.Login,name="Login"),
    path('UserRegistration/',views.UserRegistration,name="UserRegistration"), 
    path('Ajaxplace/',views.Ajaxplace,name="Ajaxplace"),
    path('ShopReg/',views.ShopReg,name="ShopReg"),
    path('DeliveryBoy/',views.DeliveryBoy,name="DeliveryBoy"),
   
     

]