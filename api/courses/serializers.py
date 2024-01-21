import datetime
from pytube import YouTube
from datetime import timedelta
from rest_framework import serializers, exceptions
from .models import Course, CourseTheme, Lesson, LessonMaterial


class CourseSerializer(serializers.ModelSerializer):
    number_of_lessons = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id',
                  'image',
                  'name',
                  'description',
                  'price',
                  'duration',
                  'number_of_lessons',
                  'created_at',
                  'is_owner']
        read_only_fields = ['user', 'number_of_lessons', 'duration', 'bought_users']

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request:
            return obj.user == request.user
        return False

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
        read_only_fields = ['course_theme', 'duration']

    def create(self, validated_data):
        video_link = validated_data.get('video_link')

        if not video_link:
            raise serializers.ValidationError({'video_link': ['Video link is required.']})
        try:
            youtube = YouTube(video_link)
            duration_seconds = youtube.length
            print(duration_seconds)
            video_time = datetime.timedelta(seconds=duration_seconds)
        except Exception as e:
            raise serializers.ValidationError({'video_link': [str(e)]})

        lesson_number = validated_data.get('lesson_number')
        if lesson_number:
            lesson, created = Lesson.objects.get_or_create(lesson_number=lesson_number,
                                                           defaults={'duration': video_time, **validated_data})
            if created:
                return lesson
            else:
                raise serializers.ValidationError({'message': ['Қате. Бұл нөмерлі сабақ бар!']})
        lesson = Lesson.objects.create(duration=video_time, **validated_data)
        return lesson

    def update(self, instance, validated_data):
        video_link = validated_data.get('video_link')

        if not video_link:
            raise serializers.ValidationError({'video_link': ['Video link is required.']})

        try:
            youtube = YouTube(video_link)
            duration_seconds = youtube.length
            instance.duration = datetime.timedelta(seconds=duration_seconds)
        except Exception as e:
            raise serializers.ValidationError({'video_link': [str(e)]})

        instance.title = validated_data.get('title', instance.title)
        lesson_number = validated_data.get('lesson_number')
        if lesson_number is not None:
            if not isinstance(lesson_number, int) or lesson_number < 0:
                raise serializers.ValidationError({'lesson_number': ['Lesson number must be a non-negative integer.']})
            lesson = Lesson.objects.get(lesson_number=lesson_number)
            if lesson:
                raise serializers.ValidationError({"message": "Қате. Бұл нөмерлі сабақ бар!"})
            instance.lesson_number = lesson_number

        instance.save()
        return instance


class LessonMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonMaterial
        fields = '__all__'
        read_only_fields = ['lesson']
