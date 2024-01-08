from django.urls import path

from api.courses import views

urlpatterns = [
    path('', views.CourseListCreateView.as_view(), name='course-list'),
    path('<str:course_name>/edit/', views.DeleteUpdateCourseView.as_view(), name='course-detail-edit'),
    path('<str:course_name>/themes/', views.CourseThemeListView.as_view(), name='course-themes-and-videos-list'),
    path('<str:course_name>/themes/<str:theme_name>/', views.RetrieveUpdateDeleteThemeView.as_view(),
         name='theme-update-delete'),
    path('<str:course_name>/themes/<str:theme_name>/lessons/', views.CreateLessonView.as_view(), name='lesson-create'),
    path('<str:course_name>/themes/<str:theme_name>/lessons/<int:lesson_id>/',
         views.RetrieveUpdateDeleteLessonView.as_view(), name='lesson-crud'),
    path('<str:course_name>/themes/<str:theme_name>/lessons/<int:lesson_id>/materials/',views.LessonMaterialCreateView.as_view(), name='lesson-material-create'),
    path('<str:course_name>/themes/<str:theme_name>/lessons/<int:lesson_id>/materials/<int:material_id>/',
         views.LessonMaterialsRUDView.as_view(), name='lesson-materials')

]
