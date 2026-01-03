from django.shortcuts import render

# Create your views here.

def Sum(request):
    if request.method == "POST":
        a = int(request.POST.get("txt_number1"))
        b = int(request.POST.get("txt_number2"))
        c = a + b
       
        return render(request,"Basics/Sum.html",{'result':c})
    else:
        return render(request,"Basics/Sum.html")

def Largest(request):
    if request.method == "POST":
        a = int(request.POST.get("txt_Number1"))
        b = int(request.POST.get("txt_Number2"))
        c = int(request.POST.get("txt_Number3"))
        if a > b  and  a > c:
            Largest = a
        elif b > a and b> c:
            Largest = b
        else:
            Largest = c
            
        return render(request,"Basics/Largest.html",{'largest':Largest})
    else:
        return render(request,"Basics/Largest.html")
    
def Calc(request):
    if request.method == "POST":
        a = int(request.POST.get("txt_Number1"))
        b = int(request.POST.get("txt_Number2"))
        btn = request.POST.get("btn_submit")
        if btn == "+" :
            c= a+b
        elif btn == "-":
            c = a-b
        elif btn == "*":
            c = a*b
        elif btn == "/":
            c = a/b
        return render(request,"Basics/Calculator.html",{'result':c})
    else:
        return render(request,"Basics/Calculator.html")