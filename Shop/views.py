from django.shortcuts import render, redirect, get_object_or_404
from Guest.models import*
from Shop.models import*
from User.models import*
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
# ML views
from django.utils import timezone
from datetime import timedelta, datetime, date
from django.db.models import Sum, Count, Q, F, FloatField, IntegerField, ExpressionWrapper, OuterRef, Subquery
from django.db.models.functions import Cast, ExtractMonth, ExtractYear, ExtractWeekDay, Coalesce
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import json
import calendar

def shop_sales_dashboard(request):
    shop_id = request.session['sid']
    
    # Get current date and time with timezone
    current_datetime = timezone.now()
    current_date = current_datetime.date()
    
    # -------------------------
    # BASIC METRICS
    # -------------------------
    
    # Total Income (All time) - using completed payments (booking_status=2)
    income = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
    )
    total_income = income['total'] or 0
    
    # Today's Income
    today_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date=current_date
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
    )['total'] or 0
    
    # This Month's Income
    month_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date__month=current_date.month,
        booking__booking_date__year=current_date.year
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
    )['total'] or 0
    
    # Last Month's Income
    last_month = current_date.replace(day=1) - timedelta(days=1)
    last_month_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date__month=last_month.month,
        booking__booking_date__year=last_month.year
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
    )['total'] or 0
    
    # Calculate growth percentage
    if last_month_income > 0:
        income_growth = ((month_income - last_month_income) / last_month_income) * 100
    else:
        income_growth = 100 if month_income > 0 else 0
    
    # Total Orders (Completed Payment)
    total_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
    ).values('booking').distinct().count()
    
    # Today's Orders
    today_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date=current_date
    ).values('booking').distinct().count()
    
    # Orders by Status (based on your model)
    pending_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status=1  # Assuming 1 is Pending/Booked but not paid
    ).values('booking').distinct().count()
    
    packed_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=3  # Packed
    ).count()
    
    shipped_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=4  # Shipped
    ).count()
    
    out_for_delivery_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=5  # Out for Delivery
    ).count()
    
    cancelled_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=7  # Cancelled
    ).count()
    
    returned_orders = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status=9  # Returned
    ).count()
    
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
        booking__booking_status__gte=2,
        booking__booking_date__gte=week_start,
        booking__booking_date__lte=current_date
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
    )['total'] or 0
    
    last_week_income = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date__gte=last_week_start,
        booking__booking_date__lte=last_week_end
    ).aggregate(
        total=Sum(ExpressionWrapper(Cast('product__product_price', output_field=FloatField()) * F('cart_qty'), output_field=FloatField()))
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
        booking__booking_status__gte=2
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
        booking__booking_status__gte=2
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
        booking__booking_status__gte=2
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
        booking__booking_status__gte=2
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

    # 1. Subquery for sold items remains the same
    sold_items = tbl_cart.objects.filter(
        product=OuterRef('product__id'),
        cart_status__gt=1
    ).values('product').annotate(
        total_sold=Sum('cart_qty')
    ).values('total_sold')

    # 2. Updated Low Stock Alert logic with ExpressionWrapper
    low_stock_products = tbl_stock.objects.filter(
        product__shop=shop_id
    ).values(
        'product__id', 
        'product__product_name'
    ).annotate(
        total_added=Sum('stock_quantity'),
        total_sold=Coalesce(Subquery(sold_items), 0),
        # Use ExpressionWrapper to explicitly define the output as an Integer
        available_qty=ExpressionWrapper(
            F('total_added') - F('total_sold'),
            output_field=IntegerField()
        )
    ).filter(
        available_qty__lte=10, 
        available_qty__gt=0
    ).order_by('available_qty')[:10]

    # 3. Updated Out of Stock logic with ExpressionWrapper
    out_of_stock = tbl_stock.objects.filter(
        product__shop=shop_id
    ).values('product').annotate(
        available=ExpressionWrapper(
            Sum('stock_quantity') - Coalesce(Subquery(sold_items), 0),
            output_field=IntegerField()
        )
    ).filter(available__lte=0).count()

    # 4. FIXED: Total Stock Value
    total_stock_value = tbl_stock.objects.filter(
    product__shop=shop_id
).annotate(
    # First, calculate the available stock per entry
    available_amount=ExpressionWrapper(
        F('stock_quantity') - Coalesce(Subquery(sold_items), 0),
        output_field=FloatField() # Use Float to allow decimal multiplication
    )
).aggregate(
    total=Sum(
        ExpressionWrapper(
            F('available_amount') * Cast('product__product_price', output_field=FloatField()),
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
        booking__booking_status__gte=2
    ).values('booking__user').distinct().count()
    
    # New Customers This Month
    new_customers = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date__month=current_date.month,
        booking__booking_date__year=current_date.year
    ).values('booking__user').distinct().count()
    
    # Repeat Customers (customers with >1 order)
    repeat_customers = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
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
    monthly_sales = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
        booking__booking_date__gte=twelve_months_ago
    ).annotate(
        month=ExtractMonth('booking__booking_date'),
        year=ExtractYear('booking__booking_date')
    ).values('month', 'year').annotate(
        total_sales=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        ),
        order_count=Count('booking__id', distinct=True)
    ).order_by('year', 'month')
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
        booking__booking_status__gte=2,
        booking__booking_date__gte=thirty_days_ago,
        booking__booking_date__lte=current_date
    ).values('booking__booking_date').annotate(
        total_sales=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        ),
        order_count=Count('booking', distinct=True)
    ).order_by('booking__booking_date')
    
    # Create a complete date range for the last 30 days
    date_range = []
    for i in range(30):
        date = current_date - timedelta(days=29-i)
        date_range.append(date)
    
    daily_data = []
    sales_dict = {item['booking__booking_date']: item for item in daily_sales if item['booking__booking_date']}
    
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
            booking__booking_status__gte=2,
            booking__booking_date__week_day=django_week_day
        ).values('booking').distinct().count()
        
        day_revenue = tbl_cart.objects.filter(
            product__shop=shop_id,
            booking__booking_status__gte=2,
            booking__booking_date__week_day=django_week_day
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
    # SALES FORECASTING & DEMAND PREDICTION
    # -------------------------
    
    # Get historical data from tbl_cart for Sales
    historical_sales = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2,
    ).values('booking__booking_date').annotate(
        total=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    ).order_by('booking__booking_date')
    
    data = []
    for s in historical_sales:
        if s['total'] and s['booking__booking_date']:
            data.append({
                "date": s['booking__booking_date'],
                "sales": float(s['total'])
            })
    
    df = pd.DataFrame(data)
    forecast = {}
    forecast_accuracy = {}
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.groupby(df['date'].dt.date)['sales'].sum().reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        if len(df) > 7:
            full_date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
            df = df.set_index('date').reindex(full_date_range).fillna(0).reset_index()
            df.rename(columns={'index': 'date'}, inplace=True)
            
            df['day_num'] = range(len(df))
            df['month'] = df['date'].dt.month
            df['weekday'] = df['date'].dt.weekday
            
            df['rolling_7'] = df['sales'].rolling(window=7, min_periods=1).mean()
            df['rolling_30'] = df['sales'].rolling(window=30, min_periods=1).mean()
            
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
                        mask = y_test.values > 0
                        if mask.any():
                            mape = np.mean(np.abs((y_test.values[mask] - predictions[mask]) / y_test.values[mask])) * 100
                            accuracy = max(0, 100 - mape)
                            forecast_accuracy[name] = round(accuracy, 2)
                        else:
                            forecast_accuracy[name] = 100.0
                    
                    last_day_num = df['day_num'].max()
                    
                    future_predictions = []
                    simulated_sales = list(df['sales'].values)
                    
                    for i in range(1, 31):
                        future_day = last_day_num + i
                        future_date = current_date + timedelta(days=i)
                        
                        r7 = np.mean(simulated_sales[-7:]) if len(simulated_sales) >= 7 else np.mean(simulated_sales)
                        r30 = np.mean(simulated_sales[-30:]) if len(simulated_sales) >= 30 else np.mean(simulated_sales)
                        
                        future_features = pd.DataFrame([[
                            future_day,
                            future_date.month,
                            future_date.weekday(),
                            r7,
                            r30
                        ]], columns=feature_cols)
                        
                        pred = model.predict(future_features)[0]
                        pred = max(0, pred)
                        future_predictions.append(pred)
                        simulated_sales.append(pred)
                    
                    forecast[name] = {
                        'values': [round(p, 2) for p in future_predictions],
                        'total': sum(future_predictions),
                        'average': np.mean(future_predictions),
                        'accuracy': forecast_accuracy.get(name, 0)
                    }
                    
    # Demand Prediction (Quantities for top products)
    top_products_demand = tbl_cart.objects.filter(
        product__shop=shop_id,
        cart_status__gte=1
    ).values('product__product_name', 'product__id').annotate(
        total_qty=Sum('cart_qty')
    ).order_by('-total_qty')[:5]

    demand_forecast = []
    for prod in top_products_demand:
        prod_id = prod['product__id']
        prod_name = prod['product__product_name']
        
        hist = tbl_cart.objects.filter(
            product__id=prod_id,
            cart_status__gte=1
        ).values('booking__booking_date').annotate(
            qty=Sum('cart_qty')
        ).order_by('booking__booking_date')
        
        d_data = []
        for h in hist:
            if h['qty'] and h['booking__booking_date']:
                d_data.append({
                    "date": h['booking__booking_date'],
                    "qty": float(h['qty'])
                })
        
        d_df = pd.DataFrame(d_data)
        if not d_df.empty and len(d_df) > 3:
            d_df['date'] = pd.to_datetime(d_df['date'])
            d_df = d_df.groupby(d_df['date'].dt.date)['qty'].sum().reset_index()
            d_df['date'] = pd.to_datetime(d_df['date'])
            
            full_date_range = pd.date_range(start=d_df['date'].min(), end=d_df['date'].max())
            d_df = d_df.set_index('date').reindex(full_date_range).fillna(0).reset_index()
            d_df.rename(columns={'index': 'date'}, inplace=True)
            
            d_df['day_num'] = range(len(d_df))
            
            X_d = d_df[['day_num']]
            y_d = d_df['qty']
            
            d_model = LinearRegression()
            d_model.fit(X_d, y_d)
            
            last_day_d = d_df['day_num'].max()
            future_qty = []
            for i in range(1, 31):
                pred = d_model.predict(pd.DataFrame([[last_day_d + i]], columns=['day_num']))[0]
                future_qty.append(max(0, pred))
            
            total_pred = int(round(sum(future_qty)))
            demand_forecast.append({
                'product_name': prod_name,
                'current_sales': prod['total_qty'],
                'predicted_demand_30d': total_pred
            })

    # -------------------------
    # ADDITIONAL METRICS
    # -------------------------
    
    # Payment Methods Distribution - If booking_status 2 (payment complete), payment method is 'Online'
    online_payments_count = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
    ).values('booking').distinct().count()
    
    online_payments_total = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                Cast('product__product_price', output_field=FloatField()) * F('cart_qty'),
                output_field=FloatField()
            )
        )
    )['total'] or 0

    payment_methods = []
    if online_payments_count > 0:
        payment_methods.append({
            'payment_method': 'Online',
            'count': online_payments_count,
            'total': online_payments_total
        })
    
    # Category Performance
    category_performance = tbl_cart.objects.filter(
        product__shop=shop_id,
        booking__booking_status__gte=2
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
        booking_status__gte=2
    ).select_related(
        'user'
    ).distinct().order_by('-booking_date')[:10]
    
    context = {
        # Basic Metrics
        "total_income": total_income,
        "today_income": today_income,
        "month_income": month_income,
        "income_growth": round(float(income_growth), 1),
        "this_week_income": this_week_income,
        "last_week_income": last_week_income,
        "wow_growth": round(float(wow_growth), 1),
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
        "retention_rate": round(float(retention_rate), 1),
        
        # Time-based Analytics
        "monthly_sales": json.dumps(monthly_data),
        "monthly_labels": json.dumps(months_list),
        "daily_sales": json.dumps(daily_data),
        "current_month": current_date.strftime('%B %Y'),
        "dow_data": json.dumps(dow_data),
        
        # Forecasting & Demand
        "forecast": forecast,
        "forecast_accuracy": forecast_accuracy,
        "has_forecast": bool(forecast),
        "demand_forecast": demand_forecast,
        
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
    shop_id = request.session['sid']
    shop = tbl_shop.objects.get(id=shop_id)
    
    # Recent products
    products = tbl_product.objects.filter(shop=shop)[:5]
    for product in products:
        total_stock = tbl_stock.objects.filter(
            product=product
        ).aggregate(total=Sum('stock_quantity'))['total'] or 0

        total_cart = tbl_cart.objects.filter(
            product=product,
            cart_status__gt=1
        ).aggregate(total=Sum('cart_qty'))['total'] or 0

        product.total_stock = max(total_stock - total_cart, 0)
    
    # Recent orders
    recent_orders = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop
    ).select_related('user').distinct().order_by('-booking_date')[:5]
    
    # Total products
    total_products = tbl_product.objects.filter(shop=shop).count()
    
    # Total orders
    total_orders = tbl_booking.objects.filter(
        tbl_cart__product__shop=shop
    ).distinct().count()
    
    # Pending orders
    pending_orders = tbl_cart.objects.filter(
        product__shop=shop,
        cart_status=0
    ).count()
    
    # Today's sales
    today = date.today()
    today_sales = tbl_cart.objects.filter(
        product__shop=shop,
        cart_status=5,
        del_date=today
    ).aggregate(
        total=Sum('product__product_price')
    )['total'] or 0
    
    context = {
        'shop': shop,
        'products': products,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_sales': today_sales,
    }
    return render(request,"Shop/Homepage.html", context)

def logout(request):
    del request.session['sid']
    return redirect("Guest:Login")

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
    categorydata = tbl_category.objects.all()
    branddata = tbl_brand.objects.all()
    productdata = tbl_product.objects.filter(shop=shopdata)
    
    for product in productdata:
        # 1. Total Stock added to the inventory
        total_stock = tbl_stock.objects.filter(
            product=product
        ).aggregate(total=Sum('stock_quantity'))['total'] or 0

        # 2. Total items actually SOLD (Status > 1 means checked out/paid)
        # If you use status=1, you are deducting items that are just sitting in users' carts!
        total_cart = tbl_cart.objects.filter(
            product=product,
            cart_status__gt=1  # Changed from =1 to __gt=1
        ).aggregate(total=Sum('cart_qty'))['total'] or 0

        # 3. Calculate current available count
        product.total_stock = max(total_stock - total_cart, 0)

    if request.method == "POST":
        name = request.POST.get("txt_name")
        details = request.POST.get("txt_details")
        photo = request.FILES.get("file_photo")
        price = request.POST.get("txt_price")
        subcategory = tbl_subcategory.objects.get(id=request.POST.get("sel_subcategory"))
        brand = tbl_brand.objects.get(id=request.POST.get("sel_brand"))
        
        tbl_product.objects.create(
            product_name=name, 
            product_details=details,
            product_photo=photo,
            product_price=price,
            shop=shopdata,
            brand=brand,
            subcategory=subcategory
        )
        
        # When redirecting, it's better to use redirect() to refresh the data
        return render(request, "Shop/Product.html", {'msg': "Data inserted.."})
    else:
        return render(request, "Shop/Product.html", {
            'categorydata': categorydata,
            'branddata': branddata,
            'product': productdata
        })
    
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

def delproduct(request, pid):
    product = tbl_product.objects.get(id=pid)
    product.delete()
    return redirect("Shop:Homepage")

def ViewBooking(request):
    # This sorts by Date first (Newest first), then by ID as a backup
    # select_related('user') helps performance by fetching user details in one query
    bookingdata = tbl_booking.objects.select_related('user').all().order_by('-booking_date', '-id')
    return render(request, "Shop/ViewBooking.html", {'bookingdata': bookingdata})

def BookingAction(request, cid, status):
    # 1. Fetch the cart item safely
    cart = get_object_or_404(tbl_cart, id=cid)
    booking = cart.booking
    user = booking.user
    email = user.user_email

    # 2. Convert status to integer (CRITICAL for the if-statements to work)
    status = int(status)
    
    subject = "Order Status Update"
    message = "" # Initialize empty message to avoid NameError

    # 3. Handle Status Updates
    if status == 3:
        cart.cart_status = 3
        cart.pack_date = date.today()
        message = f"Hello {user.user_name},\n\n📦 Your order has been packed successfully.\nIt will be shipped shortly.\n\nThank you for shopping with us."

    elif status == 4:
        cart.cart_status = 4
        cart.ship_date = date.today()
        message = f"Hello {user.user_name},\n\n🚚 Good news!\nYour order has been shipped.\nIt will reach you soon.\n\nThank you for shopping with us."

    elif status == 5:
        cart.cart_status = 5
        cart.outdel_date = date.today()
        message = f"Hello {user.user_name},\n\n🚚 Your order is out for delivery today.\nPlease keep your phone available.\n\nThank you for choosing us."

    elif status == 6:
        cart.cart_status = 6
        cart.del_date = date.today()
        message = f"Hello {user.user_name},\n\n🎉 Your order has been delivered successfully!\nWe hope you enjoy your purchase.\n\nThank you for shopping with us."

    # 4. SAVE THE CHANGES (This is what updates the DB)
    cart.save()

    # 5. SEND MAIL (Only if a message was created)
    if message:
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Email failed but status was saved: {e}")

    return redirect("Shop:ViewBooking")

def SalesReport(request):
    # 1. Initialize variables with default values
    from_date = request.POST.get("from_date")
    to_date = request.POST.get("to_date")
    
    # 2. Start with a base queryset (All bookings)
    booking_qs = tbl_booking.objects.filter(tbl_cart__product__shop=request.session['sid']).distinct()

    # 3. Apply Filter ONLY if POST and dates are provided
    if request.method == "POST" and from_date and to_date:
        booking_qs = booking_qs.filter(booking_date__range=[from_date, to_date])

    # 4. Filter Cart/Feedback based on the filtered Bookings
    # This ensures your summary cards (Total Sales, Cancels) match the date range
    total_sales = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=6).count()
    cancel_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=7).count()
    return_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=9).count()
    refund_count = tbl_cart.objects.filter(booking__in=booking_qs, cart_status=10).count()
    
    # Assuming feedback is linked to booking or product; if not, you might need a date field in tbl_feedback
    feedback_count = tbl_feedback.objects.all().count() 

    context = {
        "bookingdata": booking_qs,
        "total_sales": total_sales,
        "cancel_count": cancel_count,
        "return_count": return_count,
        "refund_count": refund_count,
        "feedback_count": feedback_count,
        "from_date": from_date, # Pass this back to keep the input filled
        "to_date": to_date      # Pass this back to keep the input filled
    }

    return render(request, "Shop/SalesReport.html", context)

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







