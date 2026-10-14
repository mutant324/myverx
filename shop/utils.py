import hashlib
import secrets

from .models import CRYPTO_RATES

# кошельки для крипто-оплаты (демо!).
# в реальном проекте тут были бы настоящие адреса и проверка транзакций через апи ноды
CRYPTO_ADDRESSES = {
    'BTC': 'bc1qmyverx0demo0wallet0addr0xr9k2vq',
    'ETH': '0xMyVeRx000000D3m0W4ll3t0000000000c0ffee',
    'USDT': 'TMyVeRxDemoWalletTRC20000000000x9k',
    'TON': 'UQmyverx_demo_wallet_ton_addr_9k2vq',
}


def hash_password(password):
    # соленый хеш, нашел такой способ в доке, так правильно хранить пароли
    salt = secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return salt + '$' + h


def check_password(password, stored):
    """проверяет пароль против того что в базе. хранится как соль$хеш"""
    if not stored:
        return False
    try:
        salt, h = stored.split('$')
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return calc == h


def crypto_amount(rub, currency):
    """переводим рубли в монеты по демо-курсу"""
    if currency not in CRYPTO_RATES or CRYPTO_RATES[currency] == 0:
        return 0
    # округляю до 6 знаков, для USDT хватает и двух но пусть будет так
    return round(rub / CRYPTO_RATES[currency], 6)
