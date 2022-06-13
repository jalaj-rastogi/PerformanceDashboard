from django.db import models

# Create your models here.
class PerformanceCategory(models.Model):
    performance_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Performance Category'
        verbose_name_plural = 'Performance Categories'


    def __str__(self):
        return self.performance_name
