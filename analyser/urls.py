from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from analyser import views

router = routers.DefaultRouter()
# router.register(r'comparison', views.ContentViewSet, basename='comparisons')
router.register(r'results', views.AnalysisResultViewSet, basename='results')
router.register(r'jobs', views.AnalysisJobViewSet)
router.register(r'scraping', views.ScrapingResultViewSet)

schema_view = get_schema_view(title='Content Rate API',
                              description='Content rater API.')
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path('/rest-test', include(analyser.urls)),
    path('schema/', schema_view),
    path('docs/', include_docs_urls(title='Content Rate API'))
]
