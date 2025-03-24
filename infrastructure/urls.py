from django.urls import path
from .views import home, report_issue, my_issues

urlpatterns = [
    path('', home, name='home'),
    path('report/', report_issue, name='report_issue'),
    path("my-issues/", my_issues, name="my_issues"),
]
