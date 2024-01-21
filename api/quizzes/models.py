from django.db import models

from api.users.models import User


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    date_published = models.DateTimeField(auto_now_add=True)
    is_trial = models.BooleanField(default=False)
    last_result = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=512)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    has_multiple_correct_answers = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Variant(models.Model):
    title = models.CharField(max_length=155)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Variant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quiz} choice {self.selected_choice} with user {self.user}"


class UserResults(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
