from django.contrib.auth.models import User, Group
from django.db import models
from rest_framework import serializers

from analyser.model.models import Comparison


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
