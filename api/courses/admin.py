from django.contrib import admin
from .models import Course, CourseTheme, Lesson, LessonMaterial, BoughtCourse

admin.site.register(Course)
admin.site.register(CourseTheme)
admin.site.register(Lesson)
admin.site.register(LessonMaterial)
admin.site.register(BoughtCourse)
