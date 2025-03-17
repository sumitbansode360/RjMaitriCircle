"""
URL configuration for MaitriCircle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from userauths.views import ProfileView, FollowView
urlpatterns = [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('admin/', admin.site.urls),
    path('user/', include('userauths.urls')),
    path('', include('post.urls')),
    path('chat/', include('chat.urls')),
    path('notifications/', include('notification.urls')),
    path('<username>/', ProfileView, name="ProfileView"),
    path('<username>/saved/', ProfileView, name="Saved"),
    path('<username>/follow/<option>/', FollowView, name="FollowView"),
]
if settings.ENVIRONMENT == "development":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 