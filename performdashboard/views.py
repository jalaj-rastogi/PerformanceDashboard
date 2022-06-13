from django.shortcuts import render
from .models import PerformanceCategory
import altair as alt

def home(request):
    category_objects = PerformanceCategory.objects.all()
    context = {
        'category_objects': category_objects
    }
    return render(request, 'index.html', context=context)