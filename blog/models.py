import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.text import slugify

STATUS = (
    ("DRAFT", "DRAFT"),
    ("PUBLISH", "PUBLISH")
)

User = get_user_model()


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    status = models.CharField(choices=STATUS, max_length=50)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='images')
    image = models.CharField(max_length=250)
    category = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blog.title)


@receiver(signals.pre_save, sender=Blog)
def populate_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)