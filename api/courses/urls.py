from django.urls import path

from api.courses import views

urlpatterns = [
    path('', views.CourseListCreateView.as_view()),
    path('<str:course_name>/themes/', views.CourseAndThemeView.as_view()),
    path('<str:course_name>/themes/<str:theme_name>/', views.ThemeAndLessonView.as_view()),
    path('<str:course_name>/themes/<str:theme_name>/lessons/<int:lesson_id>/',
         views.RetrieveUpdateDeleteLessonView.as_view()),
    path('<str:course_name>/themes/<str:theme_name>/lessons/<int:lesson_id>/materials/<int:material_id>/',
         views.LessonMaterialsRUDView.as_view())

]
