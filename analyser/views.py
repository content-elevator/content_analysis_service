from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response

from analyser import serializers
from analyser.model.models import Comparison
from analyser.serializers import ComparisonSerializer, ScrapingResultSerializer, AnalysisJobSerializer, \
    AnalysisResultSerializer, AnalysisJobCreateSerializer, AnalysisJobUpdateSerializer

from .models import AnalysisResult, AnalysisJob, ScrapingResult


comparisons = {
    1: Comparison(source_article_url='url article', source_article_title='title article', source_article_content='content article'),
    2: Comparison(source_article_url='url article', source_article_title='title article', source_article_content='content article'),
    3: Comparison(source_article_url='url article', source_article_title='title article', source_article_content='content article'),
}

def get_next_content_id():
    return max(comparisons) + 1


class ContentViewSet(viewsets.ViewSet):
    """
    API endpoint to get all content.
    """
    serializer_class = ComparisonSerializer

    def get_serializer(self):
        return self.serializer_class()

    def list(self, request):
        serializer = serializers.ComparisonSerializer(
            instance=comparisons.values(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = serializers.ComparisonSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            content = comparisons[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.ComparisonSerializer(instance=content)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            content = comparisons[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.ComparisonSerializer(
            data=request.data, instance=content)
        if serializer.is_valid():
            content = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            content = comparisons[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.ComparisonSerializer(
            data=request.data,
            instance=content,
            partial=True)
        if serializer.is_valid():
            content = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            content = comparisons[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

class AnalysisResultViewSet(viewsets.ModelViewSet):

    queryset = AnalysisResult.objects.all()
    serializer_class = AnalysisResultSerializer





class AnalysisJobViewSet(viewsets.ModelViewSet):
    queryset = AnalysisJob.objects.all()
    serializer_class = AnalysisJobSerializer
    create_serializer_class = AnalysisJobCreateSerializer
    update_serializer_class = AnalysisJobUpdateSerializer

    def get_serializer_class(self):
        """
        Determins which serializer to use
        """
        if self.action == 'create':
            if hasattr(self, 'create_serializer_class'):
                return self.create_serializer_class
        elif self.action == 'put' or self.action == 'partial_update':
            if hasattr(self, 'update_serializer_class'):
                return self.update_serializer_class
        return super().get_serializer_class()


class ScrapingResultViewSet(viewsets.ModelViewSet):
    queryset = ScrapingResult.objects.all()
    serializer_class = ScrapingResultSerializer