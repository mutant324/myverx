from datetime import datetime

from django.http import Http404
from django.shortcuts import redirect, render

from .middleware import AUTH_COOKIE, COOKIE_AGE, GUEST_COOKIE
from .models import (CartItem, Category, Order, OrderItem, CONDITIONS, GENDERS,
                     MATERIALS, Product, SEASONS, SIZES, UserProfile)
from . import utils

# тут все вьюхи сайта.
# джанговского орм у нас нет, база тянется через request.db (алхимия, см. middleware)


def all_categories(db):
    return db.query(Category).order_by(Category.id).all()


def index(request):
    """лендинг: hero + new items (слайдер группами) + style for u + about as + haw we works"""
    db = request.db
    cats = all_categories(db)
    # все товары по свежести, режем на группы по 5 (1 большая карточка + 4 маленькие).
    # группа = один слайд, листается точками и перетаскиванием мышью
    prods = db.query(Product).order_by(Product.created_at.desc(), Product.id.desc()).all()
    product_groups = [prods[i:i + 5] for i in range(0, len(prods), 5)]
    return render(request, 'shop/landing.html', {
        'categories': cats,
        'product_groups': product_groups,
    })


def catalog(request, slug=None):
    """каталог с фильтрами. все фильтры приходят GET-ом чтобы ссылкой можно было шарить"""
    db = request.db
    cats = all_categories(db)

    prods = db.query(Product)
    cat = None
    if slug:
        cat = db.query(Category).filter_by(slug=slug).first()
        if cat is None:
            raise Http404('no such category')
        prods = prods.filter_by(category_id=cat.id)

    # ---- применяем фильтры ----
    f = request.GET
    if f.get('color'):
        prods = prods.filter_by(color=f.get('color'))
    if f.get('brand'):
        prods = prods.filter_by(brand=f.get('brand'))
    if f.get('material'):
        prods = prods.filter_by(material=f.get('material'))
    if f.get('gender'):
        prods = prods.filter_by(gender=f.get('gender'))
    if f.get('size'):
        prods = prods.filter_by(size=f.get('size'))
    if f.get('condition'):
        prods = prods.filter_by(condition=f.get('condition'))
    if f.get('season'):
        prods = prods.filter_by(season=f.get('season'))
    if f.get('price_min'):
        try:
            prods = prods.filter(Product.price >= int(f.get('price_min')))
        except ValueError:
            pass  # если ввели не число то просто игнорим
    if f.get('price_max'):
        try:
            prods = prods.filter(Product.price <= int(f.get('price_max')))
        except ValueError:
            pass
    if f.get('only_sale') == 'on':
        prods = prods.filter(Product.old_price != None)  # noqa питон ругается на != None но в фильтре алхимии по другому нельзя
    q = (f.get('q') or '').strip()
    if q:
        prods = prods.filter(Product.name.ilike('%' + q + '%') | Product.brand.ilike('%' + q + '%'))

    # ---- сортировка ----
    sort = f.get('sort')
    if sort == 'price_asc':
        prods = prods.order_by(Product.price)
    elif sort == 'price_desc':
        prods = prods.order_by(Product.price.desc())
    elif sort == 'name':
        prods = prods.order_by(Product.name)
    else:
        prods = prods.order_by(Product.created_at.desc(), Product.id.desc())

    prods = prods.all()

    # ---- варианты значений для селектов фильтра (из базы а не из головы) ----
    def distinct(field):
        vals = [r[0] for r in db.query(field).distinct().all() if r[0]]
        return sorted(vals)

    brands = distinct(Product.brand)
    colors = distinct(Product.color)
    materials = distinct(Product.material)
    sizes = [s for s in SIZES if s in distinct(Product.size)]
    conditions = distinct(Product.condition)
    seasons = distinct(Product.season)

    return render(request, 'shop/catalog.html', {
        'categories': cats,
        'cat': cat,
        'products': prods,
        'brands': brands,
        'colors': colors,
        'materials': materials,
        'sizes': sizes,
        'conditions': conditions,
        'seasons': seasons,
        'genders': GENDERS,
        'filters_applied': any([f.get('color'), f.get('brand'), f.get('material'), f.get('gender'),
                                f.get('size'), f.get('condition'), f.get('season'), f.get('price_min'),
                                f.get('price_max'), f.get('only_sale'), q]),
    })


def product_page(request, product_id):
    db = request.db
    prod = db.query(Product).filter_by(id=product_id).first()
    if prod is None:
        raise Http404('no such product')
    # похожие товары из той же категории
    similar = db.query(Product).filter(
        Product.category_id == prod.category_id,
        Product.id != prod.id,
    ).limit(4).all()
    return render(request, 'shop/product.html', {
        'p': prod,
        'similar': similar,
        'categories': all_categories(db),  # для сайдбара catalogs:
    })


def search(request):
    """страница поиска. сам поиск это ilike по имени и бренду, для винтажника хватает"""
    db = request.db
    q = (request.GET.get('q') or '').strip()
    prods = []
    if q:
        prods = db.query(Product).filter(
            Product.name.ilike('%' + q + '%')
            | Product.brand.ilike('%' + q + '%')
            | Product.description.ilike('%' + q + '%')
        ).order_by(Product.id.desc()).all()
    return render(request, 'shop/search.html', {'q': q, 'products': prods})


# ================= корзина =================

def cart_add(request, product_id):
    db = request.db
    prod = db.query(Product).filter_by(id=product_id).first()
    if prod is None:
        raise Http404('no such product')

    # количество со страницы товара (?qty=N), по умолчанию 1
    try:
        qty = int(request.GET.get('qty', 1))
    except ValueError:
        qty = 1
    if qty < 1:
        qty = 1
    if qty > 99:
        qty = 99  # ну вдруг там подставили что-то безумное

    item = db.query(CartItem).filter_by(profile_id=request.profile.id, product_id=prod.id).first()
    if item is None:
        db.add(CartItem(profile_id=request.profile.id, product_id=prod.id, quantity=qty))
    else:
        item.quantity += qty
        if item.quantity > 99:
            item.quantity = 99
    db.commit()

    # "В один клик" кидает сразу в оформление
    if request.GET.get('next') == 'checkout':
        return redirect('/checkout/')
    return redirect('/cart/')


def cart_remove(request, item_id):
    db = request.db
    item = db.query(CartItem).filter_by(id=item_id, profile_id=request.profile.id).first()
    if item:
        db.delete(item)
        db.commit()
    return redirect('/cart/')


def cart_qty(request, item_id):
    """плюс/минус количество через ?d=1 или ?d=-1"""
    db = request.db
    d = 1
    if request.GET.get('d') == '-1':
        d = -1
    item = db.query(CartItem).filter_by(id=item_id, profile_id=request.profile.id).first()
    if item:
        item.quantity += d
        if item.quantity <= 0:
            db.delete(item)  # если стало ноль то удаляем строку совсем
        db.commit()
    return redirect('/cart/')


def cart_rows_and_total(db, profile):
    """собирает корзину для показа. возвращает список строк и общую сумму"""
    items = db.query(CartItem).filter_by(profile_id=profile.id).order_by(CartItem.id).all()
    rows = []
    total = 0
    for it in items:
        prod = db.query(Product).filter_by(id=it.product_id).first()
        if prod is None:
            # товар удалили из базы а строка осталась — подчищаем
            db.delete(it)
            continue
        total += prod.price * it.quantity
        rows.append({'item': it, 'prod': prod, 'sum': prod.price * it.quantity})
    db.commit()
    return rows, total


def cart_view(request):
    rows, total = cart_rows_and_total(request.db, request.profile)
    return render(request, 'shop/cart.html', {'rows': rows, 'total': total})


# ================= заказ и крипта =================

def checkout(request):
    db = request.db
    rows, total = cart_rows_and_total(db, request.profile)
    if not rows:
        return redirect('/catalog/')  # с пустой корзиной заказ не делаем

    if request.method == 'POST':
        currency = request.POST.get('currency', 'BTC')
        if currency not in utils.CRYPTO_ADDRESSES:
            currency = 'BTC'
        order = Order(
            profile_id=request.profile.id,
            total=total,
            status='waiting',
            currency=currency,
            address=utils.CRYPTO_ADDRESSES[currency],
            amount_crypto=str(utils.crypto_amount(total, currency)),
            telegram=request.POST.get('telegram', '').strip()[:50],
        )
        db.add(order)
        db.commit()  # коммитим чтобы получить order.id

        for row in rows:
            db.add(OrderItem(
                order_id=order.id,
                product_id=row['prod'].id,
                name=row['prod'].name,
                price=row['prod'].price,
                quantity=row['item'].quantity,
            ))
            # пометим что вещь забронировали — убираем из продажи пока заказ жив
            # TODO: если заказ не оплатили за 3 дня надо возвращать в продажу
        for row in rows:
            db.delete(row['item'])
        db.commit()
        return redirect('/order/%d/pay/' % order.id)

    # для формы оплаты считаем суммы в каждой монете
    variants = []
    for cur, addr in utils.CRYPTO_ADDRESSES.items():
        variants.append({
            'currency': cur,
            'amount': utils.crypto_amount(total, cur),
            'address': addr,
        })
    return render(request, 'shop/checkout.html', {'rows': rows, 'total': total, 'variants': variants})


def get_own_order(request, order_id):
    """достает заказ и проверяет что он твой.
    если заказ чужой то считаем что его вообще нет (и не палим что он существует)"""
    db = request.db
    order = db.query(Order).filter_by(id=order_id).first()
    if order is None or order.profile_id != request.profile.id:
        return None
    return order


def order_pay(request, order_id):
    order = get_own_order(request, order_id)
    if order is None:
        raise Http404('no such order')
    return render(request, 'shop/order_pay.html', {'order': order})


def order_paid(request, order_id):
    """кнопка я отправил крипту. в реальном проекте тут была бы проверка транзакции
    в блокчейне, а у нас демо поэтому просто верим юзеру"""
    if request.method != 'POST':
        return redirect('/profile/')
    order = get_own_order(request, order_id)
    if order is None:
        raise Http404('no such order')
    if order.status == 'waiting':
        order.status = 'paid'
        request.db.commit()
    return redirect('/profile/?order=ok')


# ================= профиль, вход, регистрация =================

def merge_carts(db, from_profile, to_profile):
    """переносит корзину из гостевого профиля в настоящий.
    если вещь уже есть в корзине юзера то гостевую копию просто удаляем"""
    items = db.query(CartItem).filter_by(profile_id=from_profile.id).all()
    for it in items:
        already = db.query(CartItem).filter_by(profile_id=to_profile.id, product_id=it.product_id).first()
        if already is None:
            it.profile_id = to_profile.id
        else:
            db.delete(it)
    db.commit()


def register(request):
    db = request.db
    errors = []
    data = {'username': '', 'email': '', 'first_name': '', 'last_name': '', 'birth_date': ''}

    if request.method == 'POST':
        for k in data:
            data[k] = (request.POST.get(k) or '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if len(data['username']) < 3:
            errors.append('username is too short, minimum 3 characters')
        if '@' not in data['email'] or '.' not in data['email']:
            errors.append("email doesn't look right")
        if len(password) < 6:
            errors.append('password is too short, minimum 6 characters')
        if password != password2:
            errors.append("passwords don't match")
        bd = None
        if data['birth_date']:
            try:
                bd = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                errors.append('invalid birth date')
        else:
            errors.append('enter your birth date')
        if not errors:
            if db.query(UserProfile).filter_by(username=data['username']).first():
                errors.append('this username is already taken')
            elif db.query(UserProfile).filter_by(email=data['email'], is_temporary=False).first():
                errors.append('an account with this email already exists')

        if not errors:
            user = UserProfile(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                birth_date=bd,
                is_temporary=False,
                balance=0,
                session_token=utils_secrets(),
            )
            user.password_hash = utils.hash_password(password)
            db.add(user)
            db.commit()
            # переносим корзину из гостя если он был
            if request.profile.is_temporary:
                merge_carts(db, request.profile, user)
            resp = redirect('/profile/?welcome=1')
            resp.set_cookie(AUTH_COOKIE, user.session_token, max_age=COOKIE_AGE)
            resp.delete_cookie(GUEST_COOKIE)
            return resp

    return render(request, 'shop/register.html', {'errors': errors, 'data': data})


def utils_secrets():
    # маленькая обертка чтобы не импортировать secrets в двух местах
    import secrets
    return secrets.token_hex(16)


def login_view(request):
    db = request.db
    error = ''
    username = ''
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password', '')
        user = db.query(UserProfile).filter_by(username=username, is_temporary=False).first()
        if user and utils.check_password(password, user.password_hash):
            if request.profile.is_temporary:
                merge_carts(db, request.profile, user)
            resp = redirect('/profile/')
            resp.set_cookie(AUTH_COOKIE, user.session_token, max_age=COOKIE_AGE)
            resp.delete_cookie(GUEST_COOKIE)
            return resp
        error = 'wrong username or password'
    return render(request, 'shop/login.html', {'error': error, 'username': username})


def logout_view(request):
    """выход. гостевую куку НЕ трогаем — если она была, юзер вернется в свой гостевой профиль"""
    resp = redirect('/')
    resp.delete_cookie(AUTH_COOKIE)
    return resp


def profile_view(request):
    db = request.db
    profile = request.profile
    orders = []
    if profile.is_auth():
        orders = db.query(Order).filter_by(profile_id=profile.id).order_by(Order.id.desc()).all()
    return render(request, 'shop/profile.html', {'orders': orders})
