from requests import Session, exceptions

DEFAULT_TIMEOUT = (5, 10)


class TimeoutSession(Session):
    """Сессия requests с автоматическим таймаутом."""

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return super().request(method, url, **kwargs)


_session = TimeoutSession()

get = _session.get
post = _session.post
put = _session.put
delete = _session.delete
patch = _session.patch
head = _session.head
options = _session.options

# Можно добавить другие методы или переменные, если нужно
__all__ = [
    "get", "post", "put", "delete", "patch", "head", "options",
    "Session", "exceptions",
]