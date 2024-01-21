from datetime import datetime

from .models import Quiz, Question, Variant, UserAnswer, UserResults
from rest_framework import serializers


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    request_user_has_access = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'completed', 'date_published', 'question_count', 'last_result',
                  'is_trial', 'request_user_has_access', 'max_score']
        read_only_fields = ['question_count', 'last_result', 'max_score']

    def get_request_user_has_access(self, obj):
        if obj.is_trial:
            return True
        user_profile = obj.user.profile.test_limit
        if user_profile.test_limit.timestamp() - datetime.now().timestamp() > 0:
            return True
        return False

    def get_max_score(self, obj):
        self.max_score = getattr(self, 'max_score', 0)
        self.max_score = max(obj.last_result, self.max_score)
        return self.max_score

    @staticmethod
    def get_question_count(obj):
        questions = Question.objects.filter(quiz=obj)
        return questions.count()


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'title', 'is_correct']
        read_only_fields = ['question', 'is_selected']


class QuestionSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['quiz']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['selected_choice', 'question', 'quiz', 'user']
        read_only_fields = ['user', 'quiz', 'question']


class UserResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResults
        fields = '__all__'
        read_only_fields = ['score', 'quiz', 'user', 'date_added']
