from django.db import models
from datetime import datetime

# Create your models here.
class Question(models.Model):
    q_subject                    = models.CharField(max_length=40)
    q_cat                        = models.CharField(max_length=40)
    q_rank                       = models.CharField(max_length=20)
    q_text                       = models.CharField(max_length=700,default='')
    q_option1                    = models.CharField(max_length=200,default='')
    q_option2                    = models.CharField(max_length=200,default='')
    q_option3                    = models.CharField(max_length=200,default='')
    q_option4                    = models.CharField(max_length=200,default='')
    q_answer                     = models.CharField(max_length=20)
    q_ask_time                   = models.DateTimeField(default=datetime.now, blank=True)
    no_times_ques_served         = models.IntegerField(blank=True, null=True)
    no_times_anwered_correctly   = models.IntegerField(blank=True, null=True)
    no_times_anwered_incorrectly = models.IntegerField(blank=True, null=True)
    difficulty_score             = models.DecimalField( max_digits = 5, decimal_places = 2)

    def __str__(self):
        return self.q_text

class Answer(models.Model):
    question                     = models.ForeignKey(Question, on_delete=models.CASCADE)
    ans_option                   = models.CharField(max_length=20)
    is_correct                   = models.BooleanField(default=False)
    ans_time                     = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.ans_option

class Comment(models.Model):
    c_comment                   = models.CharField(max_length=100)
    c_new_quest                 = models.CharField(max_length=100)

    def __str__(self):
        return self.c_comment


