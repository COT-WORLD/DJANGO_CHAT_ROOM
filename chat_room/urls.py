from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static, serve
import debug_toolbar
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("chat.urls")),
    path("api/", include("chat.api.urls")),
    path('accounts/', include('allauth.urls')),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
    path('__debug__/', include(debug_toolbar.urls)),
]
