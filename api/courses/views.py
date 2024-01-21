import datetime

from rest_framework import generics, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.courses.models import Course, CourseTheme, Lesson, LessonMaterial
from api.courses.serializers import CourseSerializer, CourseThemeSerializer, LessonSerializer, LessonMaterialSerializer
from api.users.permissions import IsTeacherUser, IsOwnerUser
from api.courses.permissions import IsBoughtOrFree


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['POST']:
            return [IsAuthenticated(), IsTeacherUser()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = Course.objects.all()
        serializer = CourseSerializer(queryset, many=True)
        response_data = []
        for obj in serializer.data:
            response_data.append({"id": obj["id"],
                                  "image": obj["image"],
                                  "name": obj["name"],
                                  "price": obj["price"]
                                  })
        return Response(response_data)


class CourseAndThemeView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = CourseTheme.objects.all()
    serializer_class_map = {
        "GET": CourseThemeSerializer,
        "POST": CourseThemeSerializer,
        "DELETE": CourseSerializer,
        "PUT": CourseSerializer,
    }
    lookup_url_kwarg = 'course_name'

    def get_serializer_class(self):
        """
        Return the serializer class based on the HTTP method.
        """
        return self.serializer_class_map.get(self.request.method)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsOwnerUser()]
        return []

    def get_course_object(self):
        course_name = self.kwargs.get('course_name')
        course = get_object_or_404(Course, name=course_name)
        return course

    def put(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        theme_serializer = self.get_serializer(data=request.data)
        theme_serializer.is_valid(raise_exception=True)
        self.perform_create(theme_serializer)
        return Response(theme_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        course = self.get_course_object()
        course_serializer = CourseSerializer(course).data
        course_themes = CourseTheme.objects.filter(course=course)
        course_theme_data = []

        for course_theme in course_themes:
            temp_response_lesson = []
            lessons = Lesson.objects.filter(course_theme=course_theme).order_by("lesson_number").all()
            temp_duration_of_theme = datetime.timedelta()

            for idx, lesson in enumerate(lessons, start=1):
                total_seconds = int(lesson.duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = "{:02}:{:02}".format(hours, minutes)
                temp_lesson_dict = {
                    "id": lesson.id,
                    "title": lesson.title,
                    "link": lesson.video_link,
                    "lesson_number": idx,
                    "duration": duration_str,
                    "is_prime": lesson.is_prime
                }
                temp_duration_of_theme += lesson.duration
                temp_response_lesson.append(temp_lesson_dict)

            total_seconds = int(temp_duration_of_theme.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = "{:02}:{:02}".format(hours, minutes)

            temp_theme_dict = {
                "title": course_theme.title,
                "count_lessons": lessons.count(),
                "duration": duration_str,
                'lessons': temp_response_lesson
            }
            course_theme_data.append(temp_theme_dict)

        course_serializer['course_themes'] = course_theme_data

        return Response(course_serializer)

    def perform_create(self, serializer):
        course = self.get_course_object()
        serializer.save(course=course)


class ThemeAndLessonView(generics.GenericAPIView,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    queryset = CourseTheme.objects.all()
    serializer_class_map = {
        "POST": LessonSerializer,
        "PUT": CourseThemeSerializer,
        "DELETE": CourseThemeSerializer
    }
    lookup_url_kwarg = 'theme_name'

    def get_serializer_class(self):
        """
         Return the serializer class based on the HTTP method.
        """
        return self.serializer_class_map.get(self.request.method)

    def get_permissions(self):
        return [IsOwnerUser()]

    def get_course_object(self):
        course_name = self.kwargs['course_name']
        course = get_object_or_404(Course, name=course_name)
        return course

    def get_object(self):
        course = self.get_course_object()
        self.check_object_permissions(self.request, course)
        theme_name = self.kwargs['theme_name']
        return get_object_or_404(CourseTheme, title=theme_name, course=course)

    def post(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        course = self.get_course_object()
        self.check_object_permissions(request, course)
        return self.partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        course_name = self.kwargs['course_name']
        course = get_object_or_404(Course, name=course_name)

        theme_name = self.kwargs['theme_name']
        course_theme = get_object_or_404(CourseTheme, title=theme_name, course=course)
        lesson_count = Lesson.objects.filter(course_theme=course_theme).count() + 1

        serializer.save(course_theme=course_theme, lesson_number=lesson_count)


class RetrieveUpdateDeleteLessonView(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    queryset = Lesson.objects.all()
    serializer_class_map = {
        "GET": CourseThemeSerializer,
        "POST": LessonSerializer,
        "PUT": CourseThemeSerializer,
        "DELETE": CourseThemeSerializer
    }
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_url_kwarg = 'lesson_id'

    def get_serializer_class(self):
        """
        Return the serializer class based on the HTTP method.
        """
        return self.serializer_class_map.get(self.request.method)

    def get_course_object(self):
        course_name = self.kwargs.get('course_name')
        course = Course.objects.get(name=course_name)
        return course

    def get_course_theme(self):
        course = self.get_course_object()
        theme_name = self.kwargs['theme_name']
        theme = get_object_or_404(CourseTheme, title=theme_name, course=course)
        return theme

    def get_object(self):
        theme = self.get_course_theme()
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'], course=theme)
        return lesson

    def get(self, request, *args, **kwargs):
        lesson = self.get_object()
        self.check_object_permissions(request, lesson)
        lesson_materials = LessonMaterial.objects.filter(lesson=lesson)
        serializer = LessonMaterialSerializer(lesson_materials, many=True)
        lesson_serializer = LessonSerializer(lesson)
        lesson_serializer.data['materials'] = serializer.data
        return Response({"lesson": lesson_serializer.data})

    def post(self, request, *args, **kwargs):
        return self.perform_create(request)

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE', 'POST']:
            return [IsAuthenticated(), IsOwnerUser()]
        return [IsBoughtOrFree()]

    def perform_create(self, serializer):
        lesson = self.get_object()
        serializer.save(lesson=lesson)


class LessonMaterialsRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LessonMaterial.objects.all()
    serializer_class = LessonMaterialSerializer

    http_method_names = ['patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerUser]
    lookup_url_kwarg = 'material_id'
