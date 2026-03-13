from django.shortcuts import render,redirect
from Guest.models import*
from Shop.models import*
from User.models import*

# ML views
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Count, Q, F, FloatField, IntegerField
from django.db.models.functions import Cast, ExtractMonth, ExtractYear, ExtractWeekDay
from django.db.models.expressions import ExpressionWrapper
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import json
import calendar

from Shop.models import *

def shop_sales_dashboard(request):
    shop_id = request.session['sid']
    
    # Get current date and time with timezone
    current_datetime = timezone.now()
    current_date = current_datetime.date()
    
    # -------------------------
    # BASIC METRICS
    # -------------------------
    
    # Total Income (All time) - using completed orders (cart_status=5 = Delivered)
    # Convert product_price to float for calculations
    income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5  # Delivered
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )
    total_income = income['total'] or 0
    
    # Today's Income
    today_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date=current_date
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )['total'] or 0
    
    # This Month's Income
    month_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__month=current_date.month,
        del_date__year=current_date.year
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )['total'] or 0
    
    # Last Month's Income
    last_month = current_date.replace(day=1) - timedelta(days=1)
    last_month_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__month=last_month.month,
        del_date__year=last_month.year
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )['total'] or 0
    
    # Calculate growth percentage
    if last_month_income > 0:
        income_growth = ((month_income - last_month_income) / last_month_income) * 100
    else:
        income_growth = 100 if month_income > 0 else 0
    
    # Total Orders (Delivered)
    total_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).count()
    
    # Today's Orders
    today_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date=current_date
    ).count()
    
    # Orders by Status (based on your model)
    pending_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=0  # Pending
    ).count()
    
    packed_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        pack_date__isnull=False,
        ship_date__isnull=True
    ).count()
    
    shipped_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        ship_date__isnull=False,
        outdel_date__isnull=True
    ).count()
    
    out_for_delivery_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        outdel_date__isnull=False,
        del_date__isnull=True
    ).count()
    
    cancelled_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cancel_date__isnull=False
    ).exclude(cancel_reason__isnull=True).count()
    
    returned_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        return_date__isnull=False
    ).exclude(return_reason__isnull=True).count()
    
    # Average Order Value
    avg_order_value = total_income / total_orders if total_orders > 0 else 0
    
    # -------------------------
    # WEEKLY COMPARISONS
    # -------------------------
    
    # This Week (from Monday to today)
    week_start = current_date - timedelta(days=current_date.weekday())
    
    # Last Week
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    
    this_week_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__gte=week_start,
        del_date__lte=current_date
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )['total'] or 0
    
    last_week_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__gte=last_week_start,
        del_date__lte=last_week_end
    ).aggregate(
        total=Sum(Cast('product__product_price', output_field=FloatField()))
    )['total'] or 0
    
    # Week-over-Week Growth
    if last_week_income > 0:
        wow_growth = ((this_week_income - last_week_income) / last_week_income) * 100
    else:
        wow_growth = 100 if this_week_income > 0 else 0
    
    # -------------------------
    # PRODUCT ANALYTICS
    # -------------------------
    
    # Most Bought Product
    most_product = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values(
        'product__product_name',
        'product__product_price',
        'product__id'
    ).annotate(
        total_quantity=Sum('cart_qty'),
        total_revenue=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    ).order_by('-total_quantity').first()
    
    # Most Bought Category
    most_category = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values(
        'product__subcategory__category__category_name',
        'product__subcategory__category__id'
    ).annotate(
        total_sales=Sum('cart_qty'),
        total_revenue=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    ).order_by('-total_sales').first()
    
    # Most Bought Brand
    most_brand = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values(
        'product__brand__brand_name',
        'product__brand__id'
    ).annotate(
        total_sales=Sum('cart_qty'),
        total_revenue=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    ).order_by('-total_sales').first()
    
    # Top 10 Products
    top_products = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values(
        'product__product_name',
        'product__product_price',
        'product__id'
    ).annotate(
        quantity_sold=Sum('cart_qty'),
        revenue=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    ).order_by('-quantity_sold')[:10]
    
    # -------------------------
    # STOCK MANAGEMENT
    # -------------------------
    
    # Get low stock products from tbl_stock
    low_stock_products = tbl_stock.objects.filter(
        product__shop=shop_id,
        stock_quantity__lte=10
    ).select_related('product').values(
        'product__product_name',
        'product__id',
        'stock_quantity'
    ).order_by('stock_quantity')[:10]
    
    # Get out of stock products
    out_of_stock = tbl_stock.objects.filter(
        product__shop=shop_id,
        stock_quantity=0
    ).select_related('product').values(
        'product__product_name',
        'product__id'
    ).count()
    
    # Total stock value
    total_stock_value = tbl_stock.objects.filter(
        product__shop=shop_id
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('stock_quantity') * Cast('product__product_price', output_field=FloatField()),
                output_field=FloatField()
            )
        )
    )['total'] or 0
    
    # -------------------------
    # CUSTOMER ANALYTICS
    # -------------------------
    
    # Total Customers
    total_customers = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values('booking__user').distinct().count()
    
    # New Customers This Month
    new_customers = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__month=current_date.month,
        del_date__year=current_date.year
    ).values('booking__user').distinct().count()
    
    # Repeat Customers (customers with >1 order)
    repeat_customers = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values('booking__user').annotate(
        order_count=Count('booking', distinct=True)
    ).filter(order_count__gt=1).count()
    
    # Customer Retention Rate
    retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    # -------------------------
    # TIME-BASED ANALYTICS
    # -------------------------
    
    # Monthly Sales Data (Last 12 months)
    twelve_months_ago = current_date - timedelta(days=365)
    monthly_sales = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop_id,
        booking_date__gte=twelve_months_ago,
        tbl_cart__cart_status=1
    )
    print(monthly_sales)
    monthly_data = []
    months_list = []
    for ms in monthly_sales:
        month_num = int(ms['month'])
        year_num = int(ms['year'])
        month_name = calendar.month_abbr[month_num]
        month_str = f"{month_name} {year_num}"
        months_list.append(month_str)
        monthly_data.append({
            'month': month_str,
            'sales': float(ms['total_sales']) if ms['total_sales'] else 0,
            'orders': ms['order_count']
        })
    
    # Daily Sales (Last 30 days)
    thirty_days_ago = current_date - timedelta(days=30)
    daily_sales = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5,
        del_date__gte=thirty_days_ago,
        del_date__lte=current_date
    ).values('del_date').annotate(
        total_sales=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        ),
        order_count=Count('booking', distinct=True)
    ).order_by('del_date')
    
    # Create a complete date range for the last 30 days
    date_range = []
    for i in range(30):
        date = current_date - timedelta(days=29-i)
        date_range.append(date)
    
    daily_data = []
    sales_dict = {item['del_date']: item for item in daily_sales if item['del_date']}
    
    for date in date_range:
        if date in sales_dict:
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': float(sales_dict[date]['total_sales']) if sales_dict[date]['total_sales'] else 0,
                'orders': sales_dict[date]['order_count']
            })
        else:
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': 0,
                'orders': 0
            })
    
    # -------------------------
    # STATUS-BASED ANALYTICS
    # -------------------------
    
    # Orders by Status
    orders_by_status = [
        {'status': 'Pending', 'count': pending_orders, 'color': 'warning'},
        {'status': 'Packed', 'count': packed_orders, 'color': 'info'},
        {'status': 'Shipped', 'count': shipped_orders, 'color': 'primary'},
        {'status': 'Out for Delivery', 'count': out_for_delivery_orders, 'color': 'info'},
        {'status': 'Delivered', 'count': total_orders, 'color': 'success'},
        {'status': 'Cancelled', 'count': cancelled_orders, 'color': 'danger'},
        {'status': 'Returned', 'count': returned_orders, 'color': 'secondary'},
    ]
    
    # -------------------------
    # DAY OF WEEK ANALYSIS
    # -------------------------
    
    # Get day of week distribution
    dow_data = []
    for i in range(7):
        day_name = calendar.day_name[i]
        # Django week_day: 1=Sunday, 2=Monday, ..., 7=Saturday
        django_week_day = i + 2 if i < 6 else 1
        
        day_orders = tbl_cart.objects.filter(
            product__shop=shop_id,
            cart_status=5,
            del_date__week_day=django_week_day
        ).count()
        
        day_revenue = tbl_cart.objects.filter(
            product__shop=shop_id,
            cart_status=5,
            del_date__week_day=django_week_day
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                    output_field=FloatField()
                )
            )
        )['total'] or 0
        
        dow_data.append({
            'day': day_name[:3],
            'orders': day_orders,
            'revenue': float(day_revenue)
        })
    
    # -------------------------
    # SALES FORECASTING
    # -------------------------
    
    # Get historical data from tbl_booking
    historical_sales = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop_id,
        tbl_cart__cart_status=5
    ).values('booking_date').annotate(
        total=Sum('booking_amount')
    ).order_by('booking_date')
    
    data = []
    for s in historical_sales:
        if s['total']:
            data.append({
                "date": s['booking_date'],
                "sales": float(s['total'])
            })
    
    df = pd.DataFrame(data)
    forecast = {}
    forecast_accuracy = {}
    
    if not df.empty and len(df) > 7:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create features
        df['day_num'] = range(len(df))
        df['month'] = df['date'].dt.month
        df['weekday'] = df['date'].dt.weekday
        
        # Rolling averages
        df['rolling_7'] = df['sales'].rolling(window=7, min_periods=1).mean()
        df['rolling_30'] = df['sales'].rolling(window=30, min_periods=1).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        if len(df) > 7:
            feature_cols = ['day_num', 'month', 'weekday', 'rolling_7', 'rolling_30']
            X = df[feature_cols]
            y = df['sales']
            
            split_idx = int(len(df) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            models = {
                'Linear Regression': LinearRegression(),
                'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
            }
            
            for name, model in models.items():
                if len(X_train) > 0:
                    model.fit(X_train, y_train)
                    
                    if len(y_test) > 0:
                        predictions = model.predict(X_test)
                        mask = y_test.values != 0
                        if mask.any():
                            mape = np.mean(np.abs((y_test.values[mask] - predictions[mask]) / y_test.values[mask])) * 100
                            accuracy = max(0, 100 - mape)
                            forecast_accuracy[name] = round(accuracy, 2)
                    
                    last_day_num = df['day_num'].max()
                    last_rolling_7 = df['rolling_7'].iloc[-1]
                    last_rolling_30 = df['rolling_30'].iloc[-1]
                    
                    future_predictions = []
                    for i in range(1, 8):
                        future_day = last_day_num + i
                        future_date = current_date + timedelta(days=i)
                        
                        future_features = np.array([[
                            future_day,
                            future_date.month,
                            future_date.weekday(),
                            last_rolling_7,
                            last_rolling_30
                        ]])
                        
                        pred = model.predict(future_features)[0]
                        future_predictions.append(max(0, pred))
                    
                    forecast[name] = {
                        'values': future_predictions,
                        'total': sum(future_predictions),
                        'average': np.mean(future_predictions),
                        'daily': [round(p, 2) for p in future_predictions]
                    }
    
    # -------------------------
    # ADDITIONAL METRICS
    # -------------------------
    
    # Payment Methods Distribution
    payment_methods = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop_id,
        tbl_cart__cart_status=5
    ).values('payment_method').annotate(
        count=Count('id', distinct=True),
        total=Sum('booking_amount')
    ).order_by('-total')
    
    # Category Performance
    category_performance = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5
    ).values(
        'product__subcategory__category__category_name'
    ).annotate(
        total_sales=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        ),
        total_orders=Count('booking', distinct=True)
    ).order_by('-total_sales')[:5]
    
    # Recent Transactions
    recent_transactions = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop_id,
        tbl_cart__cart_status=5
    ).select_related(
        'user', 'tbl_cart__product'
    ).distinct().order_by('-booking_date')[:10]
    
    context = {
        # Basic Metrics
        "total_income": total_income,
        "today_income": today_income,
        "month_income": month_income,
        "income_growth": round(income_growth, 1),
        "this_week_income": this_week_income,
        "last_week_income": last_week_income,
        "wow_growth": round(wow_growth, 1),
        "total_orders": total_orders,
        "today_orders": today_orders,
        
        # Order Status
        "pending_orders": pending_orders,
        "packed_orders": packed_orders,
        "shipped_orders": shipped_orders,
        "out_for_delivery_orders": out_for_delivery_orders,
        "cancelled_orders": cancelled_orders,
        "returned_orders": returned_orders,
        "orders_by_status": orders_by_status,
        
        # Product Analytics
        "avg_order_value": avg_order_value,
        "most_product": most_product,
        "most_category": most_category,
        "most_brand": most_brand,
        "top_products": top_products,
        
        # Stock Management
        "low_stock_products": low_stock_products,
        "out_of_stock": out_of_stock,
        "total_stock_value": total_stock_value,
        
        # Customer Analytics
        "total_customers": total_customers,
        "new_customers": new_customers,
        "repeat_customers": repeat_customers,
        "retention_rate": round(retention_rate, 1),
        
        # Time-based Analytics
        "monthly_sales": json.dumps(monthly_data),
        "monthly_labels": json.dumps(months_list),
        "daily_sales": json.dumps(daily_data),
        "current_month": current_date.strftime('%B %Y'),
        "dow_data": json.dumps(dow_data),
        
        # Forecasting
        "forecast": forecast,
        "forecast_accuracy": forecast_accuracy,
        "has_forecast": bool(forecast),
        
        # Additional Analytics
        "payment_methods": payment_methods,
        "category_performance": category_performance,
        "recent_transactions": recent_transactions,
        
        # Date Info
        "today": current_date,
        "now": current_datetime,
        "currency_symbol": "₹",
        "shop_id": shop_id
    }
    
    return render(request, "Shop/SalesDashboard.html", context)

# Create your views here.
def index(request):
    return render(request,"Guest/index.html")

def Homepage(request):
    return render(request,"Shop/Homepage.html")

def MyProfile(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    return render(request,"Shop/MyProfile.html",{'shop':shopdata})

def EditProfile(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    if request.method == "POST":
        name=request.POST.get("txt_name")
        email=request.POST.get("txt_email")
        contact=request.POST.get("txt_contact")
        address=request.POST.get("txt_address")
        
        shopdata.shop_name = name
        shopdata.shop_email= email
        shopdata.shop_contact= contact
        shopdata.shop_address= address
        shopdata.save()
    
        return render(request,"Shop/EditProfile.html",{'msg':"Data Updated.."})
    else:
        return render(request,"Shop/EditProfile.html",{'shop':shopdata})

def ChangePass(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    dbpass=shopdata.shop_password
    if request.method == "POST":
        password=request.POST.get("txt_password")
        newpassword=request.POST.get("txt_newpassword")
        repassword=request.POST.get("txt_repassword")
        if dbpass==password:
            if newpassword==repassword:
                shopdata.shop_password=newpassword
                shopdata.save()
                return render(request,'Shop/ChangePass.html',{'msg':"password changed..."})
            else:
                return render(request,'Shop/ChangePass.html',{'msg':"password does not match..."}) 
        else:
            return render(request,'Shop/ChangePass.html',{'msg':"invalid old password"})  
    else:
       
        return render(request,"Shop/ChangePass.html")
    
def AddStaff(request):
    staffdata=tbl_staff.objects.all()
    if request.method == "POST":
        name= request.POST.get("txt_name")
        email= request.POST.get("txt_email")
        password=request.POST.get("txt_password")
        tbl_staff.objects.create(staff_name=name, staff_email=email,staff_password=password)
        return render(request,"Shop/AddStaff.html",{'msg':"Data inserted.."})
    else:
        return render(request,"Shop/AddStaff.html",{'staffdata':staffdata})
    
def Product(request):
    shopdata = tbl_shop.objects.get(id=request.session['sid'])
    categorydata =  tbl_category.objects.all()
    branddata=tbl_brand.objects.all()
    productdata=tbl_product.objects.filter(shop=shopdata)
   
    for product in productdata:
        total_stock = tbl_stock.objects.filter(
            product=product
        ).aggregate(total=Sum('stock_quantity'))['total'] or 0

        total_cart = tbl_cart.objects.filter(
            product=product,
            cart_status=1
        ).aggregate(total=Sum('cart_qty'))['total'] or 0

        product.total_stock = max(total_stock - total_cart, 0)
    if request.method == "POST":
        name=request.POST.get("txt_name")
        details=request.POST.get("txt_details")
        photo=request.FILES.get("file_photo")
        price=request.POST.get("txt_price")
        subcategory= tbl_subcategory.objects.get(id=request.POST.get("sel_subcategory"))
        brand= tbl_brand.objects.get(id=request.POST.get("sel_brand"))
        tbl_product.objects.create(product_name=name, product_details=details,product_photo=photo,product_price=price,shop=shopdata,brand=brand,subcategory=subcategory)
        
        
        return render(request,"Shop/Product.html",{'msg':"Data inserted.."})
    else:
        return render(request,"Shop/Product.html",{'categorydata':categorydata,'branddata':branddata,'product':productdata})

def Ajaxsubcategory(request):
    subcategory=tbl_subcategory.objects.filter(category=request.GET.get('categoryId'))
    return render(request,"Shop/Ajaxsubcategory.html",{'data':subcategory})

def Gallery(request,id):
    gallerydata=tbl_gallery.objects.filter(product=id)
    productID=tbl_product.objects.get(id=id)
    if request.method == "POST":
        photo=request.FILES.get("file_photo")
        tbl_gallery.objects.create(gallery_file=photo,product=productID)
        return render(request,"Shop/Gallery.html",{'msg':"Image inserted.."})
    else:
        return render(request,"Shop/Gallery.html",{'gallery':gallerydata})

def Stock(request,id):
    stock=tbl_stock.objects.filter(product=id)
    productID=tbl_product.objects.get(id=id)
    if request.method == "POST":
        stock=request.POST.get("num_stock")
        tbl_stock.objects.create(stock_quantity=stock,product=productID)
        return render(request,"Shop/Stock.html",{'msg':"Stock inserted.."})
    else:
       
        return render(request,"Shop/Stock.html",{'stock':stock})

def delstock(request,did):
    
    tbl_stock.objects.get(id=did).delete()
    return render(request,"Shop/Stock.html",{'msg':"Data Deleted.."})

def delgallery(request,did):
    
    tbl_gallery.objects.get(id=did).delete()
    return render(request,"Shop/Gallery.html",{'msg':"Data Deleted.."})

def ViewBooking(request):
    bookingdata=tbl_booking.objects.all()
    return render(request,"Shop/ViewBooking.html",{'bookingdata':bookingdata})

def BookingAction(request, cid, status):
    cart = tbl_cart.objects.get(id=cid)
    booking = cart.booking
    user = booking.user
    email = user.user_email

    subject = "Order Status Update"

    # PACKED
    if status == 3:
        cart.cart_status = 3
        cart.pack_date = date.today()

        message = f"""
Hello {user.user_name},

📦 Your order has been packed successfully.

It will be shipped shortly.

Thank you for shopping with us.
"""

    # SHIPPED
    elif status == 4:
        cart.cart_status = 4
        cart.ship_date = date.today()

        message = f"""
Hello {user.user_name},
🚚 Good news!
Your order has been shipped.

It will reach you soon.

Thank you for shopping with us.
"""

    # OUT FOR DELIVERY
    elif status == 5:
        cart.cart_status = 5
        cart.outdel_date = date.today()

        message = f"""
Hello {user.user_name},

🚚 Your order is out for delivery today.

Please keep your phone available.

Thank you for choosing us.
"""

    # DELIVERED
    elif status == 6:
        cart.cart_status = 6
        cart.del_date = date.today()

        message = f"""
Hello {user.user_name},

🎉 Your order has been delivered successfully!

We hope you enjoy your purchase.
Thank you for shopping with us.
"""

    # SAVE CART
    cart.save()

    # SEND MAIL
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=True
    )

    return redirect("Shop:ViewBooking")

def SalesReport(request):
    bookingdata = None
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        bookingdata = tbl_booking.objects.filter(
            booking_date__range=[from_date, to_date]
        )
        

    bookingdata = tbl_booking.objects.all()

    total_sales = tbl_cart.objects.filter(cart_status=6).count()

    cancel_count = tbl_cart.objects.filter(cart_status=7).count()

    return_count = tbl_cart.objects.filter(cart_status=9).count()

    refund_count = tbl_cart.objects.filter(cart_status=10).count()

    feedback_count = tbl_feedback.objects.all().count()

    context = {
        "bookingdata": bookingdata,
        "total_sales": total_sales,
        "cancel_count": cancel_count,
        "return_count": return_count,
        "refund_count": refund_count,
        "feedback_count": feedback_count
    }

    

    return render(request, "Shop/SalesReport.html",context)
from datetime import date
def ViewRequests(request):
    cancel_requests = tbl_cart.objects.filter(cart_status=7)
    return_requests = tbl_cart.objects.filter(cart_status=9)

    return render(request, "Shop/ViewRequests.html", {
        "cancel_requests": cancel_requests,
        "return_requests": return_requests
    })


def ApproveCancel(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 8  # Cancel Approved
    cart.save()
    messages.success(request, "✅ Cancel request approved successfully.")

    send_mail(
        "Cancel Approved",
        f"Hello {user.user_name},\n\nYour cancellation request has been approved.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )

    return redirect("Shop:ViewRequests")

def ApproveReturn(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 10  # Return Approved
    cart.save()
    

    send_mail(
        "Return Approved",
        f"Hello {user.user_name},\n\nYour return request has been approved.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )
    messages.success(request, "✅ Return request approved successfully.")

    return redirect("Shop:ViewRequests")

    return redirect("Shop:RefundList")
def RejectRequest(request, cid):
    cart = tbl_cart.objects.get(id=cid)
    user = cart.booking.user

    cart.cart_status = 11  # Rejected
    cart.reject_reason = "Rejected by shop"
    cart.save()

    send_mail(
        "Request Rejected",
        f"Hello {user.user_name},\n\nYour request has been rejected by the shop.",
        settings.EMAIL_HOST_USER,
        [user.user_email],
    )
    messages.error(request, "❌ Request rejected.")
    return redirect("Shop:ViewRequests")







