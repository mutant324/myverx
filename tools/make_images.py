# -*- coding: utf-8 -*-
"""
генератор картинок товаров (svg). запускается один раз:
    python tools/make_images.py
рисует винтажные ветровки/худи/футболки/джинсы в едином стиле,
чтобы не таскать чужие фото. файлы кладутся в shop/static/shop/img/products/
"""
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'shop', 'static', 'shop', 'img', 'products')

# базовые цвета тканей по названиям из каталога
COLORS_HEX = {
    'черный': '#2e2e33',
    'белый': '#f2f1ec',
    'бежевый': '#e4d7bd',
    'серый': '#9aa0a6',
    'бордовый': '#7c2d33',
    'зеленый': '#3c6b4f',
    'синий': '#3b5a80',
    'фиолетовый': '#7a68a6',
    'коричневый': '#6b4a37',
}


def darken(hex_color, k=0.75):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


def text_color(bg):
    """цвет текста на фоне bg, чтобы читалось"""
    r = int(bg[1:3], 16)
    g = int(bg[3:5], 16)
    b = int(bg[5:7], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return '#2e2e33' if lum > 150 else '#f2f1ec'


def wrap(inner):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">'
            + inner + '</svg>')


def shadow():
    return '<ellipse cx="150" cy="272" rx="92" ry="9" fill="#000000" opacity="0.07"/>'


def logo(x, y, text, bg):
    if not text:
        return ''
    return ('<text x="%d" y="%d" font-family="Arial, sans-serif" font-weight="bold" '
            'font-size="15" text-anchor="middle" fill="%s">%s</text>'
            % (x, y, text_color(bg), text))


def sleeves_long(dark, accent):
    """длинные рукава: левый рисуем, правый зеркалим"""
    return (
        '<g id="slv">'
        '<path d="M100 96 C82 102 72 140 66 176 L58 232 C57 242 63 248 73 249 '
        'L95 251 C104 252 109 247 110 238 L114 178 L100 96 Z" fill="%s"/>'
        '<path d="M67 206 L108 212" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M64 222 L105 228" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '</g>'
        '<use href="#slv" transform="translate(300,0) scale(-1,1)"/>'
    ) % (dark, accent, accent)


def windbreaker(body, accent, logo_text):
    dark = darken(body, 0.72)
    return wrap(shadow() + sleeves_long(dark, accent) +
        # корпус
        '<path d="M100 94 C118 82 182 82 200 94 L208 240 C172 252 128 252 92 240 Z" fill="%s"/>'
        # грудная панель (колорблок как в 90-е)
        '<path d="M100 94 C118 82 182 82 200 94 L204 130 C170 140 130 140 96 130 Z" fill="%s"/>'
        # воротник-стойка
        '<path d="M126 82 L174 82 L166 99 L134 99 Z" fill="%s"/>'
        # молния
        '<line x1="150" y1="99" x2="150" y2="246" stroke="%s" stroke-width="3.5"/>'
        '<circle cx="150" cy="113" r="4" fill="%s" stroke="#ffffff" stroke-width="1"/>'
        # низ-резинка
        '<path d="M92 236 C128 248 172 248 208 236 L207 248 C172 259 128 259 93 248 Z" fill="%s"/>'
        + logo(181, 118, logo_text, accent)
        ) % (body, accent, dark, dark, dark, dark)


def hoodie(body, accent, logo_text):
    dark = darken(body, 0.72)
    darker = darken(body, 0.55)
    return wrap(shadow() + sleeves_long(dark, accent) +
        # корпус
        '<path d="M100 94 C118 82 182 82 200 94 L208 242 C172 254 128 254 92 242 Z" fill="%s"/>'
        # капюшон
        '<path d="M116 96 C120 62 180 62 184 96 C170 108 130 108 116 96 Z" fill="%s"/>'
        '<path d="M126 92 C130 72 170 72 174 92 C164 100 136 100 126 92 Z" fill="%s"/>'
        # завязки
        '<line x1="141" y1="102" x2="139" y2="126" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
        '<line x1="159" y1="102" x2="161" y2="126" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
        # карман-кенгуру
        '<path d="M118 202 L182 202 L188 246 C163 252 137 252 112 246 Z" fill="%s"/>'
        # лого на груди слева
        + logo(128, 160, logo_text, body)
        ) % (body, dark, darker, dark, dark, dark)


def tshirt(body, accent, logo_text):
    dark = darken(body, 0.8)
    return wrap(shadow() +
        # короткие рукава
        '<path d="M102 92 C88 96 80 110 76 128 L102 138 Z" fill="%s"/>'
        '<path d="M198 92 C212 96 220 110 224 128 L198 138 Z" fill="%s"/>'
        # корпус
        '<path d="M102 90 C118 80 182 80 198 90 L204 246 C168 254 132 254 96 246 Z" fill="%s"/>'
        # горловина
        '<path d="M130 88 C138 100 162 100 170 88 C162 82 138 82 130 88 Z" fill="%s"/>'
        # лого и полоска
        + logo(150, 165, logo_text, body) +
        '<path d="M100 228 L200 228" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
        ) % (dark, dark, body, dark, accent)


def jeans(denim, accent, logo_text):
    dark = darken(denim, 0.72)
    thread = '#d9b98a'
    return wrap(shadow() +
        # пояс
        '<rect x="103" y="76" width="94" height="20" rx="4" fill="%s"/>'
        '<rect x="108" y="76" width="7" height="14" fill="%s"/>'
        '<rect x="146" y="76" width="7" height="14" fill="%s"/>'
        '<rect x="185" y="76" width="7" height="14" fill="%s"/>'
        '<circle cx="172" cy="86" r="3.5" fill="#c9a36b"/>'
        # штанины
        '<path d="M103 96 L197 96 L190 254 L159 254 L151 148 L146 254 L115 254 Z" fill="%s"/>'
        # строчки
        '<path d="M107 100 L118 250" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" fill="none"/>'
        '<path d="M193 100 L182 250" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" fill="none"/>'
        # гульфик и карманы
        '<path d="M151 96 L151 130" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" fill="none"/>'
        '<path d="M110 100 C118 110 124 112 128 104" stroke="%s" stroke-width="1.6" fill="none"/>'
        '<path d="M190 100 C182 110 176 112 172 104" stroke="%s" stroke-width="1.6" fill="none"/>'
        # подвороты
        '<rect x="114" y="242" width="33" height="12" fill="%s"/>'
        '<rect x="158" y="242" width="33" height="12" fill="%s"/>'
        ) % (dark, dark, dark, dark, denim, thread, thread, thread, thread, thread, dark, dark)


def beanie(body, accent, logo_text):
    dark = darken(body, 0.72)
    ribs = ''.join(
        '<line x1="%d" y1="122" x2="%d" y2="182" stroke="%s" stroke-width="2" opacity="0.35"/>'
        % (x, x + (8 if x < 150 else -8), dark)
        for x in range(104, 200, 12)
    )
    return wrap(shadow() +
        # шапка
        '<path d="M96 190 C92 122 208 122 204 190 Z" fill="%s"/>'
        + ribs +
        # отворот
        '<path d="M94 182 L206 182 L206 208 C170 218 130 218 94 208 Z" fill="%s"/>'
        '<path d="M94 200 C130 210 170 210 206 200" stroke="%s" stroke-width="2" fill="none" opacity="0.4"/>'
        + logo(150, 202, logo_text, dark)
        ) % (body, dark, dark)


def cap(body, accent, logo_text):
    dark = darken(body, 0.72)
    return wrap(shadow() +
        # тулья
        '<path d="M90 172 C90 104 210 104 210 172 Z" fill="%s"/>'
        # швы
        '<path d="M150 106 L150 172" stroke="%s" stroke-width="2" opacity="0.5"/>'
        '<path d="M118 116 C112 132 110 152 111 172" stroke="%s" stroke-width="2" opacity="0.5" fill="none"/>'
        '<path d="M182 116 C188 132 190 152 189 172" stroke="%s" stroke-width="2" opacity="0.5" fill="none"/>'
        # козырек
        '<path d="M84 172 Q150 204 226 172 L218 188 Q150 216 84 188 Z" fill="%s"/>'
        # пуговка
        '<circle cx="150" cy="106" r="4" fill="%s"/>'
        + logo(150, 160, logo_text, body)
        ) % (body, dark, dark, dark, dark, dark)


# что рисуем: (файл, тип, цвет, акцент, лого) — данные повторяют seed.py
PRODUCTS = [
    ('p01.svg', 'jacket', 'бежевый', '#7a4a3a', 'A'),
    ('p02.svg', 'jacket', 'коричневый', '#2f2f33', 'U'),
    ('p03.svg', 'jacket', 'бордовый', '#f0e6d2', 'N'),
    ('p04.svg', 'jacket', 'серый', '#5a6474', 'R'),
    ('p05.svg', 'jacket', 'черный', '#f2f2ef', 'A'),
    ('p06.svg', 'jacket', 'черный', '#d9c7a7', 'F'),
    ('p07.svg', 'jacket', 'серый', '#3a3a3e', 'K'),
    ('p08.svg', 'jacket', 'зеленый', '#e8e0cf', 'RBK'),
    ('p09.svg', 'jacket', 'белый', '#3b5a80', 'P'),
    ('p10.svg', 'jacket', 'синий', '#20242c', 'A'),
    ('p11.svg', 'jacket', 'черный', '#f2f2ef', 'C'),
    ('p12.svg', 'jacket', 'бежевый', '#8a7f6a', 'COL'),
    ('p13.svg', 'jacket', 'бордовый', '#2e5e54', 'BD'),
    ('p14.svg', 'jacket', 'серый', '#3a4a3e', 'SS'),
    ('p15.svg', 'jacket', 'синий', '#7c2d33', 'E'),
    ('p16.svg', 'jacket', 'зеленый', '#20323e', 'R'),
    ('p17.svg', 'jacket', 'зеленый', '#d9c7a7', 'LA'),
    ('p18.svg', 'jacket', 'зеленый', '#e8e0cf', 'VA'),
    ('p19.svg', 'jacket', 'зеленый', '#24331f', ''),
    ('p20.svg', 'jacket', 'синий', '#20242c', 'L'),
    ('p21.svg', 'jacket', 'фиолетовый', '#f0e6d2', 'E'),
    ('p22.svg', 'jacket', 'серый', '#b9a8d4', 'M'),
    ('p23.svg', 'jacket', 'синий', '#e8e0cf', 'W'),
    ('p24.svg', 'jacket', 'черный', '#3b5a80', ''),
    ('p25.svg', 'hoodie', 'серый', '#7c2d33', 'C'),
    ('p26.svg', 'hoodie', 'черный', '#f2f2ef', 'N'),
    ('p27.svg', 'hoodie', 'бордовый', '#f0e6d2', 'A'),
    ('p28.svg', 'hoodie', 'зеленый', '#d9c7a7', 'CH'),
    ('p29.svg', 'tee', 'белый', '#17181a', 'RS'),
    ('p30.svg', 'tee', 'синий', '#e8e0cf', ''),
    ('p31.svg', 'tee', 'белый', '#7c2d33', ''),
    ('p32.svg', 'tee', 'зеленый', '#f2f2ef', 'USA'),
    ('p33.svg', 'jeans', 'синий', '#c9a36b', '501'),
    ('p34.svg', 'jeans', 'бежевый', '#8a7f6a', ''),
    ('p35.svg', 'jeans', 'черный', '#3a3a3e', ''),
    ('p36.svg', 'jeans', 'серый', '#f2f2ef', 'J'),
    ('p37.svg', 'beanie', 'серый', '#7c2d33', 'CH'),
    ('p38.svg', 'cap', 'синий', '#f2f2ef', 'K'),
]

DRAWERS = {
    'jacket': windbreaker,
    'hoodie': hoodie,
    'tee': tshirt,
    'jeans': jeans,
    'beanie': beanie,
    'cap': cap,
}


def box_svg():
    """посылка у двери для раздела haw we works"""
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 300">
  <rect width="420" height="300" fill="#ece5d8"/>
  <rect x="0" y="216" width="420" height="84" fill="#d8cfc0"/>
  <rect x="268" y="24" width="112" height="192" rx="4" fill="#cfd8cc"/>
  <rect x="280" y="36" width="88" height="168" rx="3" fill="#dde4da"/>
  <circle cx="352" cy="120" r="4" fill="#8a9a8e"/>
  <ellipse cx="180" cy="272" rx="108" ry="14" fill="#b9a98e"/>
  <g>
    <rect x="122" y="160" width="128" height="100" rx="4" fill="#c9a36b"/>
    <path d="M122 172 L250 172" stroke="#a9834f" stroke-width="3"/>
    <path d="M128 160 L138 148 L240 148 L250 160" fill="#b8925c"/>
    <rect x="176" y="148" width="22" height="112" fill="#e7e2d5"/>
    <text x="187" y="200" font-family="Arial, sans-serif" font-size="9" font-weight="bold"
          fill="#7a6a4f" transform="rotate(-90 187 200)">myverx</text>
    <rect x="134" y="182" width="34" height="22" rx="2" fill="#f4f1e8"/>
    <path d="M138 187 L152 187 M138 193 L164 193" stroke="#a99f8a" stroke-width="2"/>
  </g>
</svg>'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for fname, kind, color, accent, logo_text in PRODUCTS:
        body = COLORS_HEX[color]
        svg = DRAWERS[kind](body, accent, logo_text)
        with open(os.path.join(OUT_DIR, fname), 'w', encoding='utf-8') as f:
            f.write(svg)
    # посылка
    box_path = os.path.join(OUT_DIR, '..', 'box.svg')
    with open(box_path, 'w', encoding='utf-8') as f:
        f.write(box_svg())
    print('готово: %d товаров + box.svg -> %s' % (len(PRODUCTS), OUT_DIR))


if __name__ == '__main__':
    main()
