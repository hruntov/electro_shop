from io import BytesIO
import re

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'категорія'
        verbose_name_plural = 'категорії'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    video = models.URLField(blank=True, null=True, help_text="URL of the video for the product")

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=(self.id, self.slug))

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            output = BytesIO()

            img = img.resize((480, 334), Image.Resampling.LANCZOS)
            img.save(output, format='JPEG', quality=100)
            output.seek(0)

            self.image = InMemoryUploadedFile(output,
                                              'ImageField',
                                              "%s.jpg" % self.image.name.split('.')[0],
                                              'image/jpeg', output.getbuffer().nbytes, None)

        super().save(*args, **kwargs)

    def get_youtube_id(self):
        """Extracts the YouTube video ID from the URL."""
        pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)'
        match = re.search(pattern, self.video)
        return match.group(1) if match else None
