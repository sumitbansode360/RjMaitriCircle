from django.db import models
from post.models import *
import uuid
# Create your models here.

  
class PostComment(models.Model): 
    prof_pic = models.ImageField(upload_to=user_directory_path,verbose_name="commnet_pic",null=True)
    sno = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    comment = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="comments") 
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.comment[0:13] + "..." + "by" + " " + self.user.username