import datetime
from pytube import YouTube
from datetime import timedelta
from rest_framework import serializers, exceptions
from .models import Course, CourseTheme, Lesson, LessonMaterial


class CourseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    number_of_lessons = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['user', 'number_of_lessons', 'duration', 'bought_user']

    def get_number_of_lessons(self, obj):
        try:
            lessons_count = Lesson.objects.filter(course_theme__course=obj).count()
            return lessons_count
        except CourseTheme.DoesNotExist:
            return 0

    def get_duration(self, obj):
        try:
            lessons = Lesson.objects.filter(course_theme__course=obj)
            total_duration = timedelta(hours=0, minutes=0)

            for lesson in lessons:
                total_duration += lesson.duration

            hours, remainder = divmod(total_duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = "{:02}:{:02}".format(hours, minutes)

            return duration_str
        except Lesson.DoesNotExist:
            return "00:00"

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if instance.user != user:
            raise exceptions.PermissionDenied

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance

    def create(self, validated_data):
        user = self.context['request'].user
        course = Course.objects.create(**validated_data, user=user)
        return course


class CourseThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTheme
        fields = '__all__'
        read_only_fields = ['course', 'date_published']


class LessonGetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    lesson_number = serializers.IntegerField()
    duration = serializers.DurationField()
    is_prime = serializers.BooleanField()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['course_theme', 'lesson_number', 'date_published', 'duration']

    def create(self, validated_data):
        video_link = validated_data.get('video_link')
        youtube = YouTube(video_link)
        duration_seconds = youtube.length
        video_time = datetime.timedelta(seconds=duration_seconds)

        lesson = Lesson.objects.create(**validated_data, duration=video_time)
        return lesson


class LessonMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonMaterial
        fields = '__all__'
        read_only_fields = ['lesson']
