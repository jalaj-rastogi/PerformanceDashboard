from django.db import models

# Create your models here.


def get_upload_to(instance, filename):
    return 'PerformanceResults/%s/%s' % (instance.slug, filename)



class Workflow(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    result_file = models.FileField(upload_to=get_upload_to, blank=True)

    def __str__(self):
        return self.name


