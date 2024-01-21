from datetime import datetime, timedelta
from rest_framework import generics, mixins, views, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.quizzes.models import Quiz, Question, Variant, UserAnswer, UserResults
from api.quizzes.serializers import (VariantSerializer,
                                     QuizSerializer,
                                     UserAnswerSerializer,
                                     QuestionSerializer,
                                     UserResultsSerializer)
from api.quizzes.permissions import IsSuperUserOrReadOnly, IsSuperUser, IsBoughtUser


class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = []

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperUser()]
        return super().get_permissions()


class QuizDetailUpdateDeleteView(mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 generics.GenericAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsSuperUser]
    http_method_names = ['patch', 'delete']

    def get_object(self):
        return get_object_or_404(Quiz, pk=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class QuizQuestionsView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class_map = {
        'GET': QuizSerializer,
        'POST': QuestionSerializer,
    }

    def get_permissions(self):
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Return the serializer class based on the HTTP method.
        """
        return self.serializer_class_map.get(self.request.method, QuizSerializer)

    def get(self, request, *args, **kwargs):
        quiz = self.get_object()
        self.check_object_permissions(self.request, quiz)
        current_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        current_week_end = current_week_start + timedelta(days=6)
        serializer = self.get_serializer(quiz)
        questions_data = serializer.data.get('questions', [])
        response_data = [{"question_id": question['id'], "idx": idx + 1} for idx, question in enumerate(questions_data)]
        user_results = UserResults.objects.filter(
            user=request.user,
            quiz=quiz,
            date_added__range=[current_week_start, current_week_end]
        ).order_by('-date_added')
        user_results_serializer = UserResultsSerializer(user_results, many=True)
        results = [{"score": result['score'], "date": result['date_added']} for result in user_results_serializer.data]
        max_result = max(results, key=lambda x: x['score'], default=None)
        min_result = min(results, key=lambda x: x['score'], default=None)

        return Response(
            {"title": serializer.data.get('title'),
             "question_pagination": response_data,
             "user_results": results[:10],
             "user_max_result": max_result,
             "user_min_result": min_result})

    def perform_create(self, serializer):
        quiz = self.get_object()
        serializer.save(quiz=quiz)


class QuestionVariantCreateView(generics.GenericAPIView,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.RetrieveModelMixin):
    queryset = Question.objects.all()

    serializer_class_map = {
        'GET': QuestionSerializer,
        'PATCH': QuestionSerializer,
        'DELETE': QuestionSerializer,
        'POST': VariantSerializer
    }
    permission_classes = [IsSuperUserOrReadOnly]
    lookup_url_kwarg = 'question_id'

    def get_serializer_class(self):
        """
        Return the serializer class based on the HTTP method.
        """
        return self.serializer_class_map.get(self.request.method)

    def get(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj=quiz)
        question = get_object_or_404(Question, pk=self.kwargs['question_id'], quiz=quiz)
        question_serializer = QuestionSerializer(question).data
        variants = Variant.objects.filter(question=question)
        variant_serializer = VariantSerializer(variants, many=True)
        question_serializer['variants'] = variant_serializer.data
        return Response(question_serializer)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        question = Question.objects.filter(pk=self.kwargs['question_id']).first()
        serializer.save(question=question)


class VariantDeleteUpdateView(mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              generics.GenericAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer
    permission_classes = [IsSuperUser]
    lookup_url_kwarg = 'variant_id'

    def get_object(self):
        variant_instance = get_object_or_404(Variant, pk=self.kwargs['variant_id'])
        return variant_instance

    def get_queryset(self):
        instance = self.get_object()
        return instance.objects.all()


class UserAnswersView(generics.GenericAPIView, mixins.CreateModelMixin):
    model = UserAnswer
    serializer_class = UserAnswerSerializer
    permission_classes = [IsBoughtUser]
    lookup_url_kwarg = 'question_id'

    def get_quiz_object(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
        return quiz

    def get_question_object(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return question

    @staticmethod
    def delete_user_answer(quiz, question, user, selected_choice):
        user_answer_queryset = UserAnswer.objects.filter(
            quiz=quiz, question=question, user=user, selected_choice=selected_choice
        )
        if user_answer_queryset.exists():
            user_answer_queryset.delete()
            return True
        return False

    def post(self, request, *args, **kwargs):
        user = request.user
        quiz = self.get_quiz_object()
        self.check_object_permissions(request, quiz)
        question = self.get_question_object()
        serializer = UserAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected_choice = serializer.validated_data['selected_choice']
        if self.delete_user_answer(quiz, question, user, selected_choice):
            return Response(status=status.HTTP_200_OK)
        else:
            UserAnswer.objects.create(
                quiz=quiz, question=question, selected_choice=selected_choice, user=user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserAnswerCount(views.APIView):
    permission_classes = [IsSuperUserOrReadOnly]

    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs['pk'])
        user_answers = UserAnswer.objects.filter(user=request.user, quiz=quiz)
        total_score = 0

        for user_answer in user_answers:
            question = user_answer.question
            variants = Variant.objects.filter(question=question)

            variants.update(is_selected=False)

            selected_choice = user_answer.selected_choice
            if not question.has_multiple_correct_answers:
                selected_choice.is_selected = True
                if selected_choice.is_correct:
                    total_score += 1

            selected_choice.save()
            user_answer.delete()

        for user_answer in user_answers:
            question = user_answer.question
            variants = Variant.objects.filter(question=question)

            variants.update(is_selected=False)

            multiple_answers = UserAnswer.objects.filter(
                user=request.user, question=question, quiz=quiz
            )
            temp_total_score = True
            for multiple_answer in multiple_answers:
                selected_choice = multiple_answer.selected_choice
                if not selected_choice.is_correct:
                    temp_total_score = False
                    break
                selected_choice.is_selected = True
                selected_choice.save()
                multiple_answer.delete()

            if temp_total_score:
                total_score += 1
        user_results = UserResults.objects.create(quiz=quiz, score=total_score, user=request.user)
        quiz.user_result = max(quiz.user_result, total_score)
        quiz.save()

        return Response({'total_score': total_score})
