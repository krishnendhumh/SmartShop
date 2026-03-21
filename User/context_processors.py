from User.models import tbl_cart

def cart_count(request):
    """
    Add cart count to every template context
    """
    cart_count_value = 0
    
    # Check if user is logged in
    if 'uid' in request.session:
        try:
            uid = request.session.get('uid')
            # Filter cart items through booking relationship
            cart_count_value = tbl_cart.objects.filter(
                booking__user_id=uid,
                cart_status=0  # Include pending and confirmed items
            ).count()
        except Exception as e:
            print(f"Error calculating cart count: {e}")
            cart_count_value = 0
    
    return {'cart_count': cart_count_value}
