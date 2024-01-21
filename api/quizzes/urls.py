from django.urls import path

from api.quizzes import views

urlpatterns = [
    path('', views.QuizListCreateView.as_view()),
    path('<int:pk>/', views.QuizDetailUpdateDeleteView.as_view()),
    path('<int:pk>/questions/', views.QuizQuestionsView.as_view()),
    path('variants/<int:variant_id>/', views.VariantDeleteUpdateView.as_view()),
    path('<int:pk>/questions/<int:question_id>/', views.QuestionVariantCreateView.as_view()),
    path('<int:pk>/answers/<int:question_id>/', views.UserAnswersView.as_view()),
    path('results/<int:pk>/',views.UserAnswerCount.as_view())
]
