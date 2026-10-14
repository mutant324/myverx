import secrets

from sqlalchemy.exc import OperationalError

from .database import SessionMaker, init_db
from .models import UserProfile

GUEST_COOKIE = 'guest_token'
AUTH_COOKIE = 'auth_token'
COOKIE_AGE = 60 * 60 * 24 * 365  # год, ну то есть пока юзер сам куки не почистит


def new_token():
    return secrets.token_hex(16)


class TempProfileMiddleware:
    """вешает на каждого посетителя профиль.
    незалогиненному создаем временного юзера и запоминаем его в куке.
    профиль живет пока кука жива, удалил куки — получил нового гостя.
    для залогиненных ищем по AUTH_COOKIE."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # статику даже не трогаем, зачем ей профиль
        if request.path.startswith('/static/'):
            return self.get_response(request)

        db = SessionMaker()
        request.db = db
        request.profile = None
        request.set_guest_cookie = None  # сюда кладем токен если надо поставить куку гостю

        try:
            request.profile = self._find_profile(request, db)
        except OperationalError:
            # база еще не создана (забыли запустить seed) — создаем таблицы на месте
            init_db()
            request.profile = None

        if request.profile is None:
            guest = UserProfile(
                username='guest_' + new_token()[:8],
                is_temporary=True,
                balance=0,
                session_token=new_token(),
            )
            db.add(guest)
            db.commit()
            request.profile = guest
            request.set_guest_cookie = guest.session_token

        response = self.get_response(request)

        if request.set_guest_cookie:
            response.set_cookie(GUEST_COOKIE, request.set_guest_cookie, max_age=COOKIE_AGE)

        db.close()
        return response

    def _find_profile(self, request, db):
        # сначала пробуем залогиненного
        auth_token = request.COOKIES.get(AUTH_COOKIE)
        if auth_token:
            user = db.query(UserProfile).filter_by(session_token=auth_token, is_temporary=False).first()
            if user:
                return user
        # потом гостя
        guest_token = request.COOKIES.get(GUEST_COOKIE)
        if guest_token:
            guest = db.query(UserProfile).filter_by(session_token=guest_token, is_temporary=True).first()
            if guest:
                return guest
        return None
