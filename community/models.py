from django.db import models
from django.contrib.auth import get_user_model  # from accounts.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.conf import settings

# Create your models here.
class Articles(models.Model):
    title = models.CharField(max_length=40)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    image = ProcessedImageField(upload_to='images/', blank=True, null=True,
                                processors=[ResizeToFill(400, 300)],
                                format='JPEG', options={'quality': 90})
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_article')
    view_count = models.IntegerField(default=0)

class Photo(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="images/", blank=True, null=True)

class Comments(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="like_comment"
    )
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)