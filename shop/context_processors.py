from .models import CartItem


def header(request):
    """все что нужно шапке на каждой странице: профиль, баланс, число вещей в корзине"""
    profile = getattr(request, 'profile', None)
    cart_count = 0
    if profile is not None:
        cart_count = request.db.query(CartItem).filter_by(profile_id=profile.id).count()
    return {
        'profile': profile,
        'cart_count': cart_count,
        'is_auth': profile is not None and not profile.is_temporary,
    }
