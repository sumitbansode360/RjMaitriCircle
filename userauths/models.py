from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUID
from post.models import Post
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField

GENDER = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other')
)
ACCOUNT_TYPE=(
    ('Alumni', 'Alumni'),
    ('Student', 'Student')
)

STUDENT_TYPE=(
    ('Junior', 'Junior'),
    ('Under Graduate', 'Under Graduate'),
    ('Post Graduate', 'Post Graduate'),
)

def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, filename)
    return "user_{0}/{1}".format(instance.user.id, filename)

class User(AbstractUser):
    full_name = models.CharField(max_length=500, null=False, blank=False)
    username = models.CharField(max_length=500, unique= True)
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    gender = models.CharField(choices=GENDER, max_length=10)
    otp = models.CharField(max_length=100, null=True, blank=True)
    valid_doc = models.FileField(upload_to='valid_proof/')
    is_active = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    pid = ShortUUID(alphabet="abcdefghijklmnopqrstuvwxyz123")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = CloudinaryField("image", default="images/default.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=500, null=False, blank=False)
    bio = CKEditor5Field('Text', config_name='extends')
    dob = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    student_type = models.CharField(max_length=20, choices=STUDENT_TYPE)
    year_of_join = models.DateField(null=True, blank=True)
    year_of_passout = models.DateField(null=True, blank=True)
    experience = models.CharField(max_length=10000)
    skills = models.CharField(max_length=10000)
    education = models.CharField(max_length=10000)
    instagram = models.URLField(null=True, blank=True)
    git = models.URLField(null=True, blank=True)
    linkdn = models.URLField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    saved = models.ManyToManyField(Post, related_name="saved_posts", blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else:
            return f"{self.user.username}"
        
def create_user_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, *args, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
