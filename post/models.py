from django.db import models
import shortuuid
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.timezone import now
from django.conf import settings  # Import settings to use AUTH_USER_MODEL
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField


def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, ext)  # Ensure proper extension

    # Ensure the path follows Cloudinary's standard
    return "user_uploads/user_{0}/{1}".format(instance.user.id, filename)  



class Tag(models.Model):
    title = models.CharField(max_length=1000, verbose_name="Tag")
    slug = models.SlugField(null=False, unique=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def get_absolute_url(self):
        return reverse("tags", args=[self.slug])
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class Post(models.Model):
    post_id = ShortUUIDField(alphabet="abcdefghijklmnopqrstuvwxyz123", unique=True)
    image = CloudinaryField("image", null=True, blank=True)  
    caption = CKEditor5Field('Text', config_name='extends')
    posted = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag, blank=True, help_text="separate with comma")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userPost")
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)
    

    def get_absolute_url(self):
        return reverse("PostDetail", args=[self.post_id])
    
    def __str__(self):
        return self.caption
    
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")

class Stream(models.Model):
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streamFollowing")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streamUser")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="postUser")
    date = models.DateField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()
post_save.connect(Stream.add_post, sender=Post)

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")
