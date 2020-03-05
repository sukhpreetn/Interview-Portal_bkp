import datetime

from django.http import HttpResponse, request
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError

from .forms import TakeQuizForm

# Create your views here.
from .models import Question,Answer, Comment
from django.http import HttpResponse
import json
import  random

def index(request):
    return render(request, 'AIP/index.html')

def pickskill(request):
    return  render(request, 'AIP/pickskill.html')

def begin(request):
    if request.method == 'POST':
        subject = request.POST['skill']
        rank = request.POST['proficiency']
        context = {'subject':subject,'rank':rank}

        request.session['skill'] = subject
        request.session['proficiency'] = rank
        request.session['curr_difficulty_score'] = 0.00
        request.session['total_q_asked'] = 1
        request.session['total_q_ans_correct'] = 0
        request.session['counter']  = 0
        #request.session['counter'] = random.randint(1, 100)        # use this in production
        request.session['score'] = 0

        if rank == 'Adaptive':
            return render(request, 'AIP/begin.html',context)
        else:
            return render(request, 'AIP/beginsimple.html',context)


def quizsimple(request):
    subject                  = request.session['skill']
    rank                     = request.session['proficiency']
    total_q_asked            = request.session['total_q_asked']
    total_q_ans_correct      = request.session['total_q_ans_correct']
    counter                  = request.session['counter']
    score                    = request.session['score']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank)
    if questions.count() == 0 or total_q_asked == 6:
        return render(request, 'AIP/report.html',{'score':score})

    total_questions = questions.count()
    question = questions[counter]
    context = {'total_q_asked': total_q_asked, 'question': question}

    if request.method == 'POST':
        option = request.POST.get('options')
        q = Question(question.pk)
        ans = Answer()
        ans.question = q
        question.no_times_ques_served +=1

        if question.q_answer == option:
            ans.ans_option = option
            ans.is_correct = True
            question.no_times_anwered_correctly += 1
            total_q_ans_correct +=1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,no_times_anwered_correctly=question.no_times_anwered_correctly,no_times_anwered_incorrectly=question.no_times_anwered_incorrectly)
        score = (total_q_ans_correct / (total_q_asked )) * 100
        questions = Question.objects.filter(q_subject=subject, q_rank=rank)
        if questions.count() ==0 or total_q_asked == 6:
            return render(request, 'AIP/report.html',{'score':score})

        counter += 1
        total_q_asked += 1
        question =  questions[counter]

        request.session['score'] = score
        request.session['counter'] = counter
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        context = {'total_q_asked':total_q_asked,'question': question}
        return render(request, 'AIP/quizsimple.html', context)
    else:
        #this is GET flow of 1st question
        return render(request, 'AIP/quizsimple.html', context)

def quiz(request):
    subject                  = request.session['skill']
    rank                     = request.session['proficiency']
    curr_difficulty_score    = request.session['curr_difficulty_score']
    total_q_asked            = request.session['total_q_asked']
    total_q_ans_correct      = request.session['total_q_ans_correct']
    score                    = request.session['score']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
    if questions.count() == 0:
        return render(request, 'AIP/report.html',{'score':score})

    total_questions = questions.count()
    question = questions[0]
    context = {'total_q_asked': total_q_asked, 'question': question}

    if request.method == 'POST':
        option = request.POST.get('options')
        q = Question(question.pk)
        ans = Answer()
        ans.question = q
        question.no_times_ques_served +=1
        if question.q_answer == option:
            ans.ans_option = option
            ans.is_correct = True
            question.no_times_anwered_correctly += 1
            total_q_ans_correct +=1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()


        #new_difficulty_score = question.no_times_anwered_incorrectly / ( question.no_times_anwered_correctly + question.no_times_anwered_incorrectly)

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,no_times_anwered_correctly=question.no_times_anwered_correctly,no_times_anwered_incorrectly=question.no_times_anwered_incorrectly,difficulty_score=curr_difficulty_score)
        score = (total_q_ans_correct / total_q_asked) * 100

        curr_difficulty_score = question.no_times_anwered_incorrectly / ( question.no_times_anwered_correctly + question.no_times_anwered_incorrectly)

        questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
        if questions.count() == 0:
            return render(request, 'AIP/report.html' ,{'score':score})

        total_q_asked += 1
        question = questions[0]
        request.session['score'] = score
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        request.session['curr_difficulty_score'] = curr_difficulty_score
        context = {'total_q_asked':total_q_asked,'question': question}

        return render(request, 'AIP/quiz.html',context)
    else:
        return render(request, 'AIP/quiz.html',context)

def report(request):
    score = request.session['score']
    return render(request, 'AIP/report.html', {'score': score})

