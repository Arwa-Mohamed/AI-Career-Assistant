from django.urls import path

from .views import (
    CompleteInterviewView,
    InterviewHistoryView,
    StartInterviewView,
    SubmitAnswerView,
)


urlpatterns = [
    path(
        "start/",
        StartInterviewView.as_view(),
        name="start-interview",
    ),

    path(
        "questions/<int:question_id>/answer/",
        SubmitAnswerView.as_view(),
        name="submit-answer",
    ),

    path(
        "<int:session_id>/complete/",
        CompleteInterviewView.as_view(),
        name="complete-interview",
    ),

    path(
        "history/",
        InterviewHistoryView.as_view(),
        name="interview-history",
    ),
]