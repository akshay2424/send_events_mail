from django.urls import path
from event_emailer_app.views import SendEventEmails, AllDataAPIView

urlpatterns = [
    # Existing URL patterns
    path('send-event-emails/', SendEventEmails.as_view(), name='send-event-emails'),
    path('all-data/', AllDataAPIView.as_view(), name='all-data'),
]
