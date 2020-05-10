from django.db import models


# Create your models here.


class AnalysisJob(models.Model):
    class StatusChoice(models.TextChoices):
        CONFIRMED = "CONFIRMED"
        IN_QUEUE = "IN_QUEUE"
        RECEIVED = "RECEIVED"
        GOOGLE_SCRAPING_STARTED = "GOOGLE_SCRAPING_STARTED"
        URL_SCRAPING_STARTED = "URL_SCRAPING_STARTED"
        ANALYSIS_STARTED = "ANALYSIS_STARTED"
        SAVING = "SAVING"
        COMPLETED = "COMPLETED"

    user_id = models.IntegerField()
    job_status = models.CharField(
        choices=StatusChoice.choices,
        default=StatusChoice.CONFIRMED,
        max_length=250
    )


class AnalysisResult(models.Model):
    word_count_user = models.IntegerField()
    word_count_google = models.IntegerField()
    tfidf_general_score = models.FloatField()
    analysis_instance = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE,related_name='result')


class TfIdfResult(models.Model):
    analysis_instance = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='tfidf_results')
    word = models.CharField(max_length=150)
    user_score = models.FloatField()
    google_score = models.FloatField()


class ScrapingResult(models.Model):
    analysis_instance = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE)
    is_user_article = models.BooleanField()
    title = models.CharField(max_length=150)
    content = models.TextField()
