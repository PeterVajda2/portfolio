from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class SurveyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

class Employee(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    cost_center_number = models.CharField(max_length=15, blank=True, null=True)
    cost_center_name = models.CharField(max_length=150, blank=True, null=True)
    personal_number = models.IntegerField(blank=True, null=True, unique=True)
    position = models.CharField(max_length=60, blank=True, null=True)
    is_supervisor = models.BooleanField(default=True, blank=True, null=True)
    evaluator = models.CharField(max_length=40, blank=True, null=True)


class QuestionnaireTemplate(models.Model):
    name = models.CharField(max_length=50, blank=True)
    author = models.ForeignKey(to=SurveyProfile, related_name="author", on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    locked = models.BooleanField(default=False, blank=True, null=True)


class Questionnaire(models.Model):
    questionnaire = models.ForeignKey(to=QuestionnaireTemplate, on_delete=models.SET_NULL, blank=True, null=True)
    interviewer = models.ForeignKey(to=Employee, related_name="interviewer", on_delete=models.SET_NULL, blank=True, null=True)
    interviewee = models.ForeignKey(to=Employee, related_name="interviewee", on_delete=models.SET_NULL, blank=True, null=True)
    answers = models.JSONField(blank=True, default=dict)
    descriptions = models.JSONField(blank=True, default=dict)
    sent = models.BooleanField(default=False, blank=True)
    active = models.BooleanField(default=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)


class Section(models.Model):
    section_name = models.CharField(max_length=80)
    section_description = models.CharField(max_length=200)
    section_questionnaire = models.ManyToManyField(to=QuestionnaireTemplate, blank=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']


class Question(models.Model):
    text = models.CharField(max_length=200)
    section = models.ManyToManyField(to=Section, related_name="question", blank=True)
    type_of_answer = models.CharField(max_length=20, blank=True)
    weight = models.FloatField(null=True, blank=True)
    order = models.IntegerField(blank=True, null=True)
    description = models.BooleanField(default=True, blank=True, null=True)
    helper = models.JSONField(blank=True, default=dict)
    
    class Meta:
        ordering = ['id']
    

class RangedAnswer(models.Model):
    numeric_low = models.IntegerField(null=True)
    numeric_zero = models.IntegerField(null=True, blank=True)
    numeric_high = models.IntegerField(null=True)
    question = models.ManyToManyField(to=Question, related_name="ranged_answer", blank=True)
    strings = models.JSONField(blank=True, default=dict)


class TextAnswer(models.Model):
    length_limit = models.IntegerField()
    question = models.ManyToManyField(to=Question, related_name="text_answer", blank=True)