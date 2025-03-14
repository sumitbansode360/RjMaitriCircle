from django.urls import path
from .views import mark_notification_as_read
urlpatterns = [
    path('', mark_notification_as_read, name="noti-list")
]
