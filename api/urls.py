from django.urls import path, include

urlpatterns = [
    path('users/', include('api.users.urls')),
    path('courses/', include("api.courses.urls")),
    path('quizzes/', include("api.quizzes.urls"))
]
