from django.core.validators import MinValueValidator
from django.db import models

from api.users.models import User


class BoughtCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} bought {self.course.name}"


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField()
    price = models.DecimalField(validators=[MinValueValidator(0)], decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to='medias/courses/images/', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    bought_users = models.ManyToManyField(User, through=BoughtCourse, related_name='bought_courses')

    def __str__(self):
        return self.name


class CourseTheme(models.Model):
    title = models.CharField(max_length=255, null=False, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    date_published = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, null=False, db_index=True)
    lesson_number = models.IntegerField(validators=[MinValueValidator(0)], db_index=True, unique=True, null=True)
    video_link = models.URLField(null=False)
    duration = models.DurationField()
    is_prime = models.BooleanField(default=True)
    course_theme = models.ForeignKey(CourseTheme, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class LessonMaterial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    material = models.FileField(upload_to='medias/courses/materials/', null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
