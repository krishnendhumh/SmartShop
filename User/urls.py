from django.urls import path
from User import views
app_name ="User"


urlpatterns = [
    path('Homepage/',views.Homepage,name="Homepage"),
    path('MyProfile/',views.MyProfile,name="MyProfile"),
    path('EditProfile/',views.EditProfile,name="EditProfile"),
    path('ChangePass/',views.ChangePass,name="ChangePass"),
    path('Viewproduct/',views.Viewproduct,name="Viewproduct"),
    path('Viewmore/<int:id>',views.Viewmore,name="Viewmore"),
    path('Addcart/<int:id>',views.Addcart,name="Addcart"),
    path('AjaxSearch/',views.AjaxSearch,name="AjaxSearch"),
    path('Wishlist/<int:id>',views.Wishlist,name="Wishlist"),
    path('Wishlists/',views.Wishlists,name="Wishlists"),
    path('Complaint/',views.Complaint,name="Complaint"),
    path('delcomplaint/<int:id>',views.delcomplaint,name="delcomplaint"),
    path('Feedback/',views.Feedback,name="Feedback"),
    path('delfeedback/<int:id>',views.delfeedback,name="delfeedback"),
    path('MyCart/',views.Mycart, name='MyCart'),   
    path("DelCart/<int:did>", views.DelCart,name="delcart"),
    path("CartQty/", views.CartQty,name="cartqty"),
    path("payment/", views.payment,name="payment"),
    path("MyBooking/", views.MyBooking,name="MyBooking"),


]