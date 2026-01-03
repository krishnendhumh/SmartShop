from django.urls import path
from Admin import views
app_name ="Admin"


urlpatterns = [
    path('District/',views.District,name="District"),
    path("deldistrict/<int:did>/",views.deldistrict, name="deldistrict"),
    path("editdistrict/<int:eid>/",views.editdistrict, name="editdistrict"),
    path('AdminRegistration/',views.AdminRegistration,name="AdminRegistration"),
    path('deladmindata/<int:did>/',views.deladmindata, name="deladmindata"),
    path("editadmindata/<int:eid>/",views.editadmindata, name="editadmindata"),
    path('Category/',views.Category,name="Category"),
    path('delcategory/<int:did>/',views.delcategory, name="delcategory"),
    path("editcategory/<int:eid>/",views.editcategory, name="editcategory"),
    path('Place/',views.Place,name="Place"),
    path('delplace/<int:did>/',views.delplace, name="delplace"),
    path("editplace/<int:eid>/",views.editplace, name="editplace"),
    path('SubCategory/',views.SubCategory,name="SubCategory"),
    path('delsub/<int:did>/',views.delsub, name="delsub"),
    path("editsub/<int:eid>/",views.editsub, name="editsub"),
    path('Homepage/',views.Homepage,name="Homepage"),
    path('ShopVerification/',views.ShopVerification,name="ShopVerification"),
    path('accept/<int:aid>',views.accept,name="accept"),
    path('reject/<int:rid>',views.reject,name="reject"),
    path('Brand/',views.Brand,name="Brand"),
    path('delbrand/<int:did>/',views.delbrand, name="delbrand"),
    path("editbrand/<int:eid>/",views.editbrand, name="editbrand"),
    path("Viewcomplaint/", views.Viewcomplaint, name="Viewcomplaint"),
    path("replycomplaint/<int:id>/", views.replycomplaint, name="replycomplaint"),
    path("Viewfeedback/", views.Viewfeedback, name="Viewfeedback"),
    

    
]