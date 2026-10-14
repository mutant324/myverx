from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

# справочники для фильтров и для сидинга (сайт на английском)
COLORS = ['black', 'white', 'beige', 'grey', 'burgundy', 'green', 'blue', 'purple', 'brown']
SIZES = ['XS', 'S', 'M', 'L', 'XL']
GENDERS = ['unisex', 'male', 'female']
CONDITIONS = ['10/10', '9/10', '8/10', '7/10']
SEASONS = ['mid-season', 'winter', 'summer']
MATERIALS = ['polyester', 'cotton', 'nylon', 'wool', 'denim', 'acrylic']

CRYPTO_RATES = {
    # курсы для демо оплаты, в реале надо дергать апи курса.
    # цены на сайте в долларах (как в макете), поэтому курсы тоже в $
    'BTC': 67000,
    'ETH': 2600,
    'USDT': 1,
    'TON': 5,
}


class UserProfile(Base):
    """юзер сайта. бывает постоянный (после регистрации) и временный (гость по кукам)"""
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120))
    password_hash = Column(String(200))  # у гостя пароля нет поэтому nullable
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date)
    balance = Column(Integer, default=0)  # в рублях целым числом, без копеек
    is_temporary = Column(Boolean, default=False)
    session_token = Column(String(64), unique=True, nullable=False)  # по нему ищем по куке
    created_at = Column(DateTime, default=datetime.now)

    @property
    def full_name(self):
        # иногда одно из имен пустое, склеиваем аккуратно
        parts = [x for x in [self.first_name, self.last_name] if x]
        return ' '.join(parts) if parts else self.username

    def is_auth(self):
        return not self.is_temporary


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)   # как показываем людям
    slug = Column(String(50), unique=True, nullable=False)  # для урла типа /catalog/outerwear/

    def count(self, db):
        # сколько товаров в категории, для лендинга
        from sqlalchemy import func
        return db.query(func.count(Product.id)).filter_by(category_id=self.id).scalar()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    brand = Column(String(50))
    article = Column(String(20))  # артикул типа MV-1042
    category_id = Column(Integer, ForeignKey('categories.id'))
    price = Column(Integer, nullable=False)
    old_price = Column(Integer)  # если была скидка, то тут старая цена
    color = Column(String(30))
    material = Column(String(30))
    gender = Column(String(10))
    size = Column(String(5))
    condition = Column(String(10))  # состояние типа 9/10
    season = Column(String(20))
    description = Column(String(500))
    image = Column(String(200))  # путь от статики типа shop/img/products/p01.svg
    created_at = Column(DateTime, default=datetime.now)

    category = relationship('Category')

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(100 - self.price * 100 / self.old_price)
        return 0


class CartItem(Base):
    """строка корзины, привязана к профилю (в т.ч. к гостевому)"""
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)

    product = relationship('Product')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    total = Column(Integer, nullable=False)
    status = Column(String(20), default='waiting')  # waiting / paid / sent
    currency = Column(String(10))       # BTC / ETH / USDT / TON
    address = Column(String(120))       # куда переводить
    amount_crypto = Column(String(30))  # сколько монет, строкой чтобы не терять знаки
    telegram = Column(String(50))       # куда писать если что
    created_at = Column(DateTime, default=datetime.now)

    items = relationship('OrderItem')

    STATUS_LABELS = {
        'waiting': 'awaiting payment',
        'paid': 'paid',
        'sent': 'shipped',
    }

    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)


class OrderItem(Base):
    """товар внутри заказа, цену сохраняем на момент покупки"""
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    name = Column(String(120))  # копия имени, вдруг товар потом удалят
    price = Column(Integer)
    quantity = Column(Integer, default=1)

    product = relationship('Product')
