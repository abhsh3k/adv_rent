from django.contrib import admin
from django.contrib.admin import autodiscover
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from toolx.admin import admin_site

autodiscover()

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('tools.urls')),
    path('rentals/', include('rentals.urls')),
    path('reviews/', include('reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)