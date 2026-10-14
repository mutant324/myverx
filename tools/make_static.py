# -*- coding: utf-8 -*-
"""
сборка статичного слепка сайта для GitHub Pages:
    ./venv/Scripts/python.exe tools/make_static.py
сервер должен быть запущен (python manage.py runserver).
результат кладется в _site/, оттуда пушится в ветку gh-pages.

django тут не нужен: страницы тянем HTTP-ом с локального сервера,
а поиск в статике работает через search-index.json прямо в браузере.
"""
import json
import os
import re
import shutil
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # чтобы import shop работал из tools/

BASE = 'http://127.0.0.1:8765'
SITE = '_site'
PREFIX = '/myverx'

# все GET-страницы сайта -> файлы для GitHub Pages
pages = {
    '/': 'index.html',
    '/catalog/': 'catalog/index.html',
    '/catalog/outerwear/': 'catalog/outerwear/index.html',
    '/catalog/denim/': 'catalog/denim/index.html',
    '/catalog/hoodies/': 'catalog/hoodies/index.html',
    '/search/': 'search/index.html',
    '/cart/': 'cart/index.html',
    '/login/': 'login/index.html',
    '/register/': 'register/index.html',
    '/profile/': 'profile/index.html',
}
for i in range(1, 22):
    pages[f'/product/{i}/'] = f'product/{i}/index.html'


def rewrite(html):
    # сайт на Pages живет в подпапке /myverx/, абсолютные пути чиним
    html = html.replace('href="/', f'href="{PREFIX}/')
    html = html.replace("href='/", f"href='{PREFIX}/")
    html = html.replace('src="/', f'src="{PREFIX}/')
    html = html.replace('action="/', f'action="{PREFIX}/')
    return html


# --- 1. тянем страницы ---
fails = []
for url, rel in pages.items():
    try:
        html = urllib.request.urlopen(BASE + url, timeout=10).read().decode('utf-8')
    except Exception as e:
        fails.append((url, str(e)))
        continue
    p = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(rewrite(html))

# --- 2. статика целиком ---
shutil.copytree('shop/static', os.path.join(SITE, 'static'), dirs_exist_ok=True)

# --- 3. json-индекс товаров для живого поиска в статике ---
# (импортируем алхимию напрямую, django не нужен)
from shop.database import SessionMaker
from shop.models import Product

db = SessionMaker()
data = []
for p in db.query(Product).order_by(Product.id).all():
    data.append({
        'id': p.id,
        'name': p.name,
        'brand': p.brand,
        'color': p.color,
        'size': p.size,
        'price': p.price,
        'condition': p.condition,
        'image': PREFIX + '/static/' + p.image,
        'url': f'{PREFIX}/product/{p.id}/',
    })
with open(os.path.join(SITE, 'search-index.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

# --- 4. оживляем поиск на статичной странице /search/ ---
search_path = os.path.join(SITE, 'search', 'index.html')
with open(search_path, encoding='utf-8') as f:
    s = f.read()

inject = '''<section class="landing-section" id="jsSearchResults" hidden>
    <h1 class="marker sec-title" id="jsTitle">search</h1>
    <p class="hand-sub" id="jsCount"></p>
    <div class="product-grid" id="jsGrid"></div>
</section>
<script>
(function () {
    var data = __PRODUCTS_JSON__;
    var q = (new URLSearchParams(location.search).get('q') || '').trim().toLowerCase();
    if (!q) return; /* пустой запрос — остаемся на подсказке */

    /* прячем статичную заглушку, показываем результаты */
    var stub = document.querySelector('.landing-section');
    if (stub) stub.hidden = true;
    var box = document.getElementById('jsSearchResults');
    box.hidden = false;

    var found = data.filter(function (p) {
        return (p.name + ' ' + p.brand + ' ' + p.color).toLowerCase().indexOf(q) !== -1;
    });
    document.getElementById('jsTitle').textContent = 'search: \\u00ab' + q + '\\u00bb';
    document.getElementById('jsCount').textContent = found.length
        ? 'found: ' + found.length + ' items'
        : 'nothing for \\u00ab' + q + '\\u00bb :(';

    var grid = document.getElementById('jsGrid');
    found.forEach(function (p) {
        var card = document.createElement('a');
        card.className = 'product-card';
        card.href = p.url;
        card.innerHTML =
            '<div class="ph-wrap"><img src="' + p.image + '" alt="" loading="lazy"></div>' +
            '<div class="card-row"><div class="card-names">' +
            '<span class="p-name">' + p.name + '</span>' +
            '<span class="p-meta">' + p.size + ' \\u00b7 ' + p.color + '</span></div>' +
            '<div class="card-buy"><span class="p-price">' + p.price + '$</span></div>' +
            '</div>';
        grid.appendChild(card);
    });
})();
</script>'''

marker = '</main>'
assert marker in s, 'не нашел </main> на странице поиска'
s = s.replace(marker, inject.replace('__PRODUCTS_JSON__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')) + '\n' + marker, 1)
with open(search_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(s)

print('страниц:', len(pages) - len(fails), '| неудач:', fails or 'нет')
print('товаров в поисковом индексе:', len(data))
