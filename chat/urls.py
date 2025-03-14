from django.urls import path
from chat.views import chat_view, get_or_create_chatroom, chat_file_upload
urlpatterns = [
    path('', chat_view, name="home"),
    path('<username>/', get_or_create_chatroom, name="start-chat"),
    path('room/<chatroom_name>/', chat_view, name="chatroom"),
    path('fileupload/<chatroom_name>/', chat_file_upload, name="chat-file-upload"),

]


