from django.db import models
from django.conf import settings  # Import settings to use AUTH_USER_MODEL
from userauths.models import User
import shortuuid
import os
# Create your models here.

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, default=shortuuid.uuid)
    users_online = models.ManyToManyField(User, related_name="online_in_groups", blank=True)
    members = models.ManyToManyField(User, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    body = models.CharField(max_length=3000, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        if self.body:
            return f'{self.user.username} : {self.body}'
        else:
            return f'{self.user.username} : {self.filename}'

    class Meta:
        ordering = ['-created']

    @property
    def is_image(self):
        if self.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
            return True
        else:
            return False
