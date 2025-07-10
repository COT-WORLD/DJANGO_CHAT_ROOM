# from django.core.cache import cache
# from django.http import HttpRequest
# from django.urls import reverse
# from django.utils.cache import get_cache_key


# def invalidate_view_cache(view_name, key_prefix, kwargs=None):
#     fake_request = HttpRequest()
#     fake_request.method = "GET"
#     fake_request.META["SERVER_NAME"] = "localhost"
#     fake_request.META["SERVER_PORT"] = "8000"

#     path = reverse(view_name, kwargs=kwargs) if kwargs else reverse(view_name)
#     fake_request.path = path

#     cache_key = get_cache_key(fake_request, key_prefix=key_prefix)
#     if cache_key:
#         cache.delete(cache_key)
