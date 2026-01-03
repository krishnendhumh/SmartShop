from django.urls import path
from Shop import views
app_name ="Shop"


urlpatterns = [
    path('Homepage/',views.Homepage,name="Homepage"),
    path('MyProfile/',views.MyProfile,name="MyProfile"),
    path('EditProfile/',views.EditProfile,name="EditProfile"),
    path('ChangePass/',views.ChangePass,name="ChangePass"),
    path('AddStaff/',views.AddStaff,name="AddStaff"),
    path('Product/',views.Product,name="Product"),
    path('Ajaxsubcategory/',views.Ajaxsubcategory,name="Ajaxsubcategory"),
    path('Gallery/<int:id>',views.Gallery,name="Gallery"),
    path('Stock/<int:id>',views.Stock,name="Stock"),
    path('delstock/<int:did>',views.delstock,name="delstock"),
    path('delgallery/<int:did>',views.delgallery,name="delgallery"),
    path('ViewBooking/',views.ViewBooking,name="ViewBooking"),
    path('BookingAction/<int:cid>/<int:status>',views.BookingAction,name="BookingAction"),


]