from django.http import Http404
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.courses.models import Course, CourseTheme, Lesson, LessonMaterial
from api.courses.serializers import CourseSerializer, CourseThemeSerializer, LessonSerializer, LessonMaterialSerializer, \
    LessonGetSerializer
from api.users.permissions import IsTeacherUser, IsOwnerUser
from api.courses.permissions import IsBoughtUserOrOwner


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['POST']:
            return [IsAuthenticated(), IsTeacherUser()]
        return super().get_permissions()


class DeleteUpdateCourseView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerUser, IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']
    lookup_url_kwarg = 'course_name'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        course_name = self.kwargs.get('course_name')
        return get_object_or_404(Course, name=course_name, user=self.request.user)


class CourseThemeListView(
    generics.ListCreateAPIView

):
    queryset = CourseTheme.objects.all()
    serializer_class = CourseThemeSerializer
    lookup_field = 'course_name'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['POST']:
            return [IsAuthenticated(), IsOwnerUser()]
        return super().get_permissions()

    def get_queryset(self):
        course_name = self.kwargs.get('course_name')
        try:
            course = Course.objects.get(name=course_name)
            course_themes = CourseTheme.objects.filter(course=course)
            return course_themes
        except Course.DoesNotExist:
            raise Http404("Course not found")

    def create(self, request, *args, **kwargs):
        course_name = kwargs.get('course_name')
        course = Course.objects.get(name=course_name)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, course)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, course):
        serializer.save(course=course)

    def list(self, request, *args, **kwargs):
        course_name = self.kwargs.get('course_name')
        course = get_object_or_404(Course, name=course_name)
        course_themes = CourseTheme.objects.filter(course=course)
        course_serializer = CourseSerializer(course)

        response_data = {
            "course": course_serializer.data['name'],
            "course_themes": [],
        }

        for course_theme in course_themes:
            theme_data = CourseThemeSerializer(course_theme).data
            lesson_qs = Lesson.objects.filter(course_theme=course_theme)
            lesson_serializer = LessonGetSerializer(lesson_qs, many=True)
            theme_data['lessons'] = lesson_serializer.data
            response_data["course_themes"].append(theme_data)

        return Response(response_data)


class RetrieveUpdateDeleteThemeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseTheme.objects.all()
    serializer_class = CourseThemeSerializer
    permission_classes = [IsOwnerUser, IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']
    lookup_url_kwarg = 'theme_name'

    def get_object(self):
        course_theme = self.kwargs['course_name']
        course = get_object_or_404(Course, name=course_theme)
        theme_name = self.kwargs['theme_name']
        return get_object_or_404(CourseTheme, title=theme_name, course=course)

    def get_permissions(self):
        return super().get_permissions()


class CreateLessonView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerUser, IsAuthenticated]
    lookup_url_kwarg = 'theme_name'

    def perform_create(self, serializer):
        course_name = self.kwargs['course_name']
        course = get_object_or_404(Course, name=course_name)

        theme_name = self.kwargs['theme_name']
        course_theme = get_object_or_404(CourseTheme, title=theme_name, course=course)
        lesson_count = Lesson.objects.filter(course_theme=course_theme).count() + 1

        serializer.save(course_theme=course_theme, lesson_number=lesson_count)


class RetrieveUpdateDeleteLessonView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_url_kwarg = 'lesson_id'

    def get_object(self):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'])
        return lesson

    def get(self, request, *args, **kwargs):
        lesson = self.get_object()
        lesson_materials = LessonMaterial.objects.filter(lesson=lesson)
        serializer = LessonMaterialSerializer(lesson_materials, many=True)
        lesson_serializer = LessonSerializer(lesson)
        return Response({"lesson": lesson_serializer.data, "materials": serializer.data})

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerUser()]
        return [IsBoughtUserOrOwner()]


class LessonMaterialCreateView(generics.CreateAPIView):
    queryset = LessonMaterial.objects.all()
    serializer_class = LessonMaterialSerializer
    lookup_url_kwarg = 'lesson_id'

    def perform_create(self, serializer):
        lesson = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, pk=lesson)
        serializer.save(lesson=lesson)


class LessonMaterialsRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LessonMaterial.objects.all()
    serializer_class = LessonMaterialSerializer

    http_method_names = ['get', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerUser]
    lookup_url_kwarg = 'material_id'
