from django.urls import path
from Basics import views

urlpatterns = [
    path('Sum/',views.Sum,name="Sum"),
    path('Largest/',views.Largest,name="Largest"),
    path('Calc/',views.Calc,name="Calc"),
]