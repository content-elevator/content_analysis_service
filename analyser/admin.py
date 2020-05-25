from django.contrib import admin
from .models import AnalysisJob, AnalysisResult, TfIdfResult, ScrapingResult

# Register your models here.
admin.site.register(AnalysisJob)
admin.site.register(AnalysisResult)
admin.site.register(TfIdfResult)
admin.site.register(ScrapingResult)
