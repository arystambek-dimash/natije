from django.contrib import admin
from .models import Quiz, Question, Variant, UserAnswer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Variant)
admin.site.register(UserAnswer)
