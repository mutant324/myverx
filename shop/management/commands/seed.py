"""
наполнение базы тестовыми данными:
    python manage.py seed
повторно не задублирует, а с --force пересоздаст все с нуля

фото товаров лежат в shop/static/shop/img/products/ (пришли реальные фото,
именование p01..p16 = market, new1..new5 = карусель new items на лендинге).
сайт полностью на английском, поэтому и данные товаров на английском
"""
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from shop.database import SessionMaker, init_db
from shop.models import Category, Product

CATEGORIES = [
    {'name': 'outerwear', 'slug': 'outerwear'},
    {'name': 'denim', 'slug': 'denim'},
    {'name': 'hoodies', 'slug': 'hoodies'},
]

# новые поступления (карусель new items на лендинге) — у них самые свежие даты
NEW_ITEMS = [
    dict(img='new1', name='sweater Reebok', brand='Reebok', cat='hoodies', price=100,
         color='grey', material='cotton', gender='unisex', size='L', condition='9/10',
         season='mid-season',
         description='Reebok International is an American company that manufactures '
                     'sportswear, footwear, and accessories. Vintage sweatshirt with '
                     'a big logo, condition 9/10.'),
    dict(img='new2', name='sweater Sincere', brand='Sincere', cat='hoodies', price=56,
         color='grey', material='cotton', gender='male', size='L', condition='9/10',
         season='mid-season',
         description='Grey sweatshirt by Sincere Cult. Relaxed fit, dropped shoulders, '
                     'original chest print — not a reprint.'),
    dict(img='new3', name='Reebok half-zip sweat', brand='Reebok', cat='hoodies', price=47,
         color='green', material='cotton', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Half-zip sweatshirt, cream top and dark green bottom. Soft, '
                     'brushed inside, fits the way it should.'),
    dict(img='new4', name='Denim jacket racing', brand='Vintage', cat='denim', price=58,
         color='blue', material='denim', gender='male', size='L', condition='8/10',
         season='mid-season',
         description='Denim jacket with red and white racing stripes. The patina is '
                     'real — earned, not styled.'),
    dict(img='new5', name='Black denim jacket', brand='Vintage', cat='denim', price=55,
         color='black', material='denim', gender='unisex', size='L', condition='8/10',
         season='mid-season',
         description='Black denim, four patch pockets. Heavy, warm, and ready for '
                     'another twenty years.'),
]

# ветровки из стока (market) — p01..p16 по алфавиту файлов
P = [
    dict(img='p01', name='Nike grey panel anorak', brand='Nike', cat='outerwear', price=38,
         color='black', material='nylon', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Grey-paneled Nike anorak with a half-zip. That proper 2000s '
                     'nylon rustle.'),
    dict(img='p02', name='Adidas two-tone track', brand='Adidas', cat='outerwear', price=45,
         color='black', material='polyester', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Black and cream Adidas jacket with sleeve stripes. Classic for '
                     'trains, cafes and yard tournaments.'),
    dict(img='p03', name='Beige utility overshirt', brand='Vintage', cat='outerwear', price=34,
         color='beige', material='cotton', gender='male', size='XL', condition='8/10',
         season='mid-season',
         description='Oversized beige utility jacket. More pockets than you need — '
                     'but you can never have too many.'),
    dict(img='p04', name='Umbro chocolate windbreaker', brand='Umbro', cat='outerwear', price=36,
         color='brown', material='polyester', gender='male', size='L', condition='8/10',
         season='mid-season',
         description='Chocolate brown Umbro windbreaker. Slight cuff wear that only '
                     'makes it look better.'),
    dict(img='p05', name='Reebok colorblock windbreaker', brand='Reebok', cat='outerwear', price=42,
         color='grey', material='polyester', gender='unisex', size='L', condition='9/10',
         season='mid-season',
         description='90s colorblock: grey, graphite and milk white. A combo that '
                     'never gets old.'),
    dict(img='p06', name='Reebok colorblock v2', brand='Reebok', cat='outerwear', price=40,
         color='grey', material='polyester', gender='male', size='M', condition='9/10',
         season='mid-season',
         description='Same colorblock, different cut. If you know — you know.'),
    dict(img='p07', name='Cherry retro windbreaker', brand='Vintage', cat='outerwear', price=44,
         color='burgundy', material='nylon', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Cherry-red retro windbreaker with cream inserts. You can '
                     'almost hear the nylon rustle.'),
    dict(img='p08', name='Reebok khaki vintage shell', brand='Reebok', cat='outerwear', price=39,
         color='green', material='polyester', gender='male', size='L', condition='8/10',
         season='mid-season',
         description='Khaki Reebok shell with a big chest print. A warehouse find, '
                     'barely worn.'),
    dict(img='p09', name='Adidas black-white half-zip', brand='Adidas', cat='outerwear', price=37,
         color='black', material='polyester', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Half-zip, black and white colorblock. Simple and spot on.'),
    dict(img='p10', name='Washed denim trucker', brand='Lee', cat='denim', price=52,
         color='blue', material='denim', gender='male', size='M', condition='8/10',
         season='mid-season',
         description='Lee trucker jacket in a heavy wash. Faded buttons, workwear '
                     'fit, city attitude.'),
    dict(img='p11', name='Sport navy-white jacket', brand='Vintage', cat='outerwear', price=35,
         color='white', material='polyester', gender='unisex', size='L', condition='9/10',
         season='summer',
         description='White summer shell with navy panels. Light enough to crush '
                     'into a fist.'),
    dict(img='p12', name='Nike black anorak', brand='Nike', cat='outerwear', price=41,
         color='black', material='nylon', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Black Nike anorak with a grey chest panel. The hood hides '
                     'away in the collar.'),
    dict(img='p13', name='Adidas striped half-zip', brand='Adidas', cat='outerwear', price=43,
         color='black', material='cotton', gender='unisex', size='M', condition='9/10',
         season='mid-season',
         description='Three stripes down the sleeves, half-zip front. Dense cotton '
                     'that holds its shape.'),
    dict(img='p14', name='Cream satin bomber', brand='Vintage', cat='outerwear', price=48,
         color='beige', material='nylon', gender='female', size='S', condition='9/10',
         season='mid-season',
         description='Cream satin bomber with embroidery. Looks way more expensive '
                     'than it is.'),
    dict(img='p15', name='Navy-white summer shell', brand='Vintage', cat='outerwear', price=33,
         color='white', material='nylon', gender='unisex', size='M', condition='9/10',
         season='summer',
         description='Summer shell: white top, deep navy bottom. Saves you from the '
                     'wind, not from compliments.'),
    dict(img='p16', name='Sage panel half-zip', brand='Vintage', cat='outerwear', price=36,
         color='green', material='polyester', gender='unisex', size='L', condition='8/10',
         season='mid-season',
         description='Black anorak with a sage chest panel. Rare color — you won\'t '
                     'find a second one.'),
]

ART_NUM = 1000  # артикулы сгенерим простым счетчиком


class Command(BaseCommand):
    help = 'наполняет базу категориями и товарами'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='пересоздать все с нуля')

    def handle(self, *args, **options):
        init_db()
        db = SessionMaker()

        if options['force']:
            db.query(Product).delete()
            db.query(Category).delete()
            db.commit()

        if db.query(Product).count() > 0:
            self.stdout.write('товары уже есть, ничего не делаю (для пересоздания: --force)')
            return

        # категории (если уже есть — не дублируем, а переиспользуем)
        cats = {}
        for c in CATEGORIES:
            exists = db.query(Category).filter_by(slug=c['slug']).first()
            if exists:
                cats[c['slug']] = exists
                continue
            cat = Category(name=c['name'], slug=c['slug'])
            db.add(cat)
            db.commit()
            cats[c['slug']] = cat

        def add_product(item, hours_ago):
            global ART_NUM  # без этого питон думает что ART_NUM локальная и падает
            ART_NUM += 1
            db.add(Product(
                name=item['name'],
                brand=item['brand'],
                article='MV-%d' % ART_NUM,
                category_id=cats[item['cat']].id,
                price=item['price'],
                old_price=item.get('old_price'),
                color=item['color'],
                material=item['material'],
                gender=item['gender'],
                size=item['size'],
                condition=item['condition'],
                season=item['season'],
                description=item['description'],
                image='shop/img/products/' + item['img'] + '.png',
                created_at=datetime.now() - timedelta(hours=hours_ago),
            ))

        # new items — самые свежие (порядок как в карусели на лендинге)
        for i, item in enumerate(NEW_ITEMS):
            add_product(item, i * 3)

        # сток — постарше
        for i, item in enumerate(P):
            add_product(item, 24 + i * 7)

        db.commit()

        self.stdout.write('готово: %d категорий, %d товаров' % (len(CATEGORIES), len(NEW_ITEMS) + len(P)))
