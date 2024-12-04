
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('master_admin/', admin.site.urls),
    path('',include('testapp.urls')),
    path('ipd/',include('IPDapp.urls')),
    path('api/',include('testapp.api.urls')),
    path('api-func/',include('testapp.func_api.urls')),
    path('accounts/',include('django.contrib.auth.urls')),
    path('usermanagementapp/',include('usermanagementapp.urls')),
    path('auto/',include('ramapp.urls')),
    # path('__debug__/', include('debug_toolbar.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
