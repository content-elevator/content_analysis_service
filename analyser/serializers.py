from django.contrib.auth.models import User, Group
from django.db import models
from rest_framework import serializers

from analyser.model.models import Comparison
from analyser.models import AnalysisJob, ScrapingResult
from analyser.models import AnalysisResult
from analyser.models import TfIdfResult


class ComparisonSerializer(serializers.Serializer):
    source_article_url = models.CharField(max_length=250)
    source_article_title = models.CharField(max_length=250)
    source_article_content = models.CharField(max_length=100000)

    def create(self, validated_data):
        return Comparison(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance


class ScrapingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingResult
        fields = ('analysis_instance', 'is_user_article', 'is_last_google_article', 'title', 'content')


class TfIdfResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TfIdfResult
        fields = ('word', 'user_score', 'google_score')


class AnalysisResultSerializer(serializers.ModelSerializer):
    tfidf_results = TfIdfResultSerializer(many=True)

    class Meta:
        model = AnalysisResult
        fields = ('word_count_user', 'word_count_google', 'tfidf_general_score', 'analysis_instance', 'tfidf_results')


class AnalysisJobSerializer(serializers.ModelSerializer):
    result = AnalysisResultSerializer(many=True)

    class Meta:
        model = AnalysisJob
        fields = ('id', 'user_id', 'job_status', 'url', 'query', 'result')

class AnalysisJobUpdateSerializer(serializers.ModelSerializer):


    class Meta:
        model = AnalysisJob
        fields = ('id', 'job_status', 'url', 'query')

class AnalysisJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisJob
        fields = ('id','user_id', 'url', 'query')
