from django.urls import path
from .views import IngestDataView, LiveStateView, AlertListView

urlpatterns = [
    path('ingest/', IngestDataView.as_view(), name='ingest'),
    path('live-state/', LiveStateView.as_view(), name='live-state'),
    path('alerts/', AlertListView.as_view(), name='alerts'),
]
