// тут весь js сайта. его немного но он весь по делу

document.addEventListener('DOMContentLoaded', function () {

    // ================= поиск в шапке =================
    // по ТЗ: первый клик — поле появляется, второй клик (если поле пустое) — пропадает.
    // если в поле что-то есть, клик по кнопке отправляет поиск
    var form = document.getElementById('searchForm');
    var btn = document.getElementById('searchToggle');
    var input = document.getElementById('searchInput');

    if (form && btn && input) {
        btn.addEventListener('click', function (e) {
            if (!form.classList.contains('open')) {
                // первый клик — открываем поле и не отправляем форму
                e.preventDefault();
                form.classList.add('open');
                input.focus();
            } else if (input.value.trim() === '') {
                // второй клик по пустому полю — закрываем
                e.preventDefault();
                form.classList.remove('open');
            }
            // иначе форма сама отправится, preventDefault не нужен
        });

        // если на странице поиска что-то ввели, поле сразу открыто
        if (input.value !== '') {
            form.classList.add('open');
        }
    }

    // ================= панель фильтров в каталоге =================
    var fBtn = document.getElementById('filtersToggle');
    var fPanel = document.getElementById('filtersPanel');

    if (fBtn && fPanel) {
        if (fPanel.classList.contains('open')) {
            fBtn.classList.add('open'); // стрелка сразу перевернута если фильтры показаны
        }
        fBtn.addEventListener('click', function () {
            var isOpen = fPanel.classList.toggle('open');
            fBtn.classList.toggle('open', isOpen);
        });
    }

    // ================= кнопка copy на странице оплаты =================
    var copyBtn = document.getElementById('copyAddressBtn');
    var addr = document.getElementById('payAddress');

    if (copyBtn && addr) {
        copyBtn.addEventListener('click', function () {
            var text = addr.textContent.trim();
            // clipboard работает не везде, поэтому с запасным вариантом
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function () {
                    copyBtn.textContent = 'ok ✓';
                    setTimeout(function () { copyBtn.textContent = 'copy'; }, 1500);
                });
            } else {
                // старый способ через выделение
                var range = document.createRange();
                range.selectNodeContents(addr);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('copy');
                copyBtn.textContent = 'ok ✓';
                setTimeout(function () { copyBtn.textContent = 'copy'; }, 1500);
            }
        });
    }

    // ================= страница товара: количество и табы =================

    // счетчик количества, кнопки меняют qty в ссылках "в корзину" и "в один клик"
    var qtyVal = document.getElementById('qtyVal');
    var qtyMinus = document.getElementById('qtyMinus');
    var qtyPlus = document.getElementById('qtyPlus');
    var buyNow = document.getElementById('buyNow');
    var addToCart = document.getElementById('addToCart');

    if (qtyVal && qtyMinus && qtyPlus && buyNow && addToCart) {
        var qty = 1;
        // в ссылках qty зашит как ?qty=N, тупо заменяем число через регэксп
        function updateQtyLinks() {
            buyNow.href = buyNow.href.replace(/qty=\d+/, 'qty=' + qty);
            addToCart.href = addToCart.href.replace(/qty=\d+/, 'qty=' + qty);
        }
        qtyPlus.addEventListener('click', function () {
            if (qty < 99) qty += 1;
            qtyVal.textContent = qty;
            updateQtyLinks();
        });
        qtyMinus.addEventListener('click', function () {
            if (qty > 1) qty -= 1;
            qtyVal.textContent = qty;
            updateQtyLinks();
        });
    }

    // табы Description / Specifications / Delivery and Payment
    var tabs = document.querySelectorAll('.item-tabs .tab');
    if (tabs.length) {
        tabs.forEach(function (btn) {
            btn.addEventListener('click', function () {
                // все табы гасим, активным делаем нажатый
                tabs.forEach(function (b) { b.classList.remove('active'); });
                btn.classList.add('active');
                // прячем все панели, показываем нужную
                document.querySelectorAll('.tab-pane').forEach(function (pane) {
                    pane.hidden = (pane.id !== 'tab-' + btn.getAttribute('data-tab'));
                    pane.classList.toggle('active', !pane.hidden);
                });
            });
        });
    }

    // ================= слайдер new items: группы листаются точками и драгом мыши =================
    var slider = document.getElementById('newSlider');
    var dotsBox = document.getElementById('newDots');

    if (slider && dotsBox) {
        var track = slider.querySelector('.slider-track');
        var dots = dotsBox.querySelectorAll('.dot');
        var idx = 0;
        var dragStarted = false;
        var moved = 0;

        function goTo(i) {
            var n = dots.length;
            idx = Math.max(0, Math.min(i, n - 1));
            track.style.transform = 'translateX(-' + (idx * 100) + '%)';
            dots.forEach(function (d, k) {
                d.className = 'dot' + (k === idx ? ' active' : '');
            });
        }

        // клик по точке — переход к конкретной группе
        dots.forEach(function (d) {
            d.addEventListener('click', function () {
                goTo(parseInt(d.getAttribute('data-idx'), 10));
            });
        });

        // перетаскивание мышью: зажал и повел справа налево (или обратно)
        slider.addEventListener('mousedown', function (e) {
            dragStarted = true;
            moved = 0;
            slider.classList.add('dragging');
            slider._startX = e.clientX;
            e.preventDefault(); // чтобы не выделялся текст и не драгались картинки
        });

        window.addEventListener('mousemove', function (e) {
            if (!dragStarted) return;
            moved = e.clientX - slider._startX;
            // тянем трек вместе с мышью
            var pos = -(idx * 100) + (moved / slider.clientWidth) * 100;
            track.style.transform = 'translateX(' + pos + '%)';
        });

        window.addEventListener('mouseup', function () {
            if (!dragStarted) return;
            dragStarted = false;
            slider.classList.remove('dragging');
            // дотянули больше трети ширины — листаем, иначе возврат на место
            if (moved < -slider.clientWidth / 3) {
                goTo(idx + 1);
            } else if (moved > slider.clientWidth / 3) {
                goTo(idx - 1);
            } else {
                goTo(idx);
            }
        });

        // если после драга произошел клик по карточке — отменяем переход по ссылке
        slider.addEventListener('click', function (e) {
            if (Math.abs(moved) > 10) {
                e.preventDefault();
                e.stopPropagation();
                moved = 0;
            }
        }, true);

        // картинки внутри слайдера не должны перетаскиваться браузером
        slider.querySelectorAll('img').forEach(function (im) {
            im.setAttribute('draggable', 'false');
        });
    }

});
