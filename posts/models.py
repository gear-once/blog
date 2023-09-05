from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager



class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
                      .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,unique_for_date='publish')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    
    tags = TaggableManager()
    image = models.ImageField(upload_to='images/%Y/%m/%d/', null=True, blank=True)
    posts_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='posts_liked',
                                        blank=True)

    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
               args=[self.publish.year,
                    self.publish.month,
                    self.publish.day,
                    self.slug])
    
    #for Create_Post_View
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
#________________COMMENT CLASS_____________________

class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='post_comments',
                               null=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.user} on {self.post}'
