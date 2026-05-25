from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone


MAX_ATTEMPTS = 5
BLOCK_MINUTES = 15
WINDOW_MINUTES = 10


def _cache_key(phone):
    return f"auth_attempts:{phone}"


def is_blocked(phone):
    data = cache.get(_cache_key(phone))
    print(data)
    if not data:
        return False
    if data['count'] >= MAX_ATTEMPTS:
        return timezone.now() < data['blocked_until']
    return False


def register_failed_attempt(phone):
    now = timezone.now()
    data = cache.get(_cache_key(phone), {
        'count': 0,
        'first_attempt': now,
        'blocked_until': None
    })

    data['count'] += 1

    if data['count'] >= MAX_ATTEMPTS:
        data['blocked_until'] = now + timedelta(minutes=BLOCK_MINUTES)

    cache.set(_cache_key(phone), data, timeout=BLOCK_MINUTES * 60)


def reset_attempts(phone):
    cache.delete(_cache_key(phone))
