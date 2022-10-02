from django.urls import path


from .views import (
    ClassView,
    FeedView,
)




urlpatterns = [
    path('classes/', ClassView.as_view(), name='classes'),
    path('feed/', FeedView.as_view(), name='search'),
]