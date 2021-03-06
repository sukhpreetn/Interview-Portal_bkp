import datetime
from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from django.views import generic

from .models import Question, Answer, Result,Quiz
from django.http import HttpResponse
import json
import random
import csv, io
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from .forms import QuestionForm
from django.contrib.auth.models import User
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,UpdateView)

def index(request):
    return render(request, 'AIP/index.html')


def pickskill(request):
    request.session['user'] = request.user.get_full_name()
    user = request.session['user']
    Result.objects.create(c_user=user)
    context = {'user':user}
    return render(request, 'AIP/pickskill.html',context)

def begin(request):
    if request.method == 'POST':
        subject = request.POST['skill']
        rank = request.POST['proficiency']
        context = {'subject': subject, 'rank': rank}
        request.session['skill'] = subject
        request.session['proficiency'] = rank
        request.session['curr_difficulty_score'] = 1
        request.session['total_q_asked'] = 1
        request.session['total_q_ans_correct'] = 0
        request.session['counter'] = 0
        cat_dict = {'Introduction': 0, 'Syntax': 0, 'OOPS': 0, 'NativeDataTypes': 0, 'FileAndExceptionHandling': 0,
                    'Function': 0, 'Advanced': 0}
        request.session['cat_dict'] = cat_dict
        request.session['score'] = 0

        if rank == 'Adaptive':
            return render(request, 'AIP/begin.html', context)
        else:
            return render(request, 'AIP/beginsimple.html', context)


def quizsimple(request):
    subject = request.session['skill']
    rank = request.session['proficiency']
    total_q_asked = request.session['total_q_asked']
    total_q_ans_correct = request.session['total_q_ans_correct']
    counter = request.session['counter']
    score = request.session['score']
    cat_dict = request.session['cat_dict']
    user = request.session['user']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank)
    max = Question.objects.filter(q_subject=subject, q_rank=rank).count()
    ind = random.randint(1, max)
    question = questions[ind]
    context = {'total_q_asked': total_q_asked, 'question': question}
    if request.method == 'POST':
        option = request.POST.get('options')
        q = Question(question.pk)
        ans = Answer()
        ans.question = q
        question.no_times_ques_served += 1

        total_q_asked += 1
        if question.q_answer == option:
            ans.ans_option = option
            ans.is_correct = True
            question.no_times_anwered_correctly += 1
            total_q_ans_correct += 1
            cat_dict[question.q_cat] += 1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,
                                                no_times_anwered_correctly=question.no_times_anwered_correctly,
                                                no_times_anwered_incorrectly=question.no_times_anwered_incorrectly)
        if counter == 20 or request.POST.get('END') == 'STOP':
            score1 = (total_q_ans_correct / (total_q_asked - 1)) * 100
            score = round(score1)
            cat_scores = json.dumps(cat_dict)
            Result.objects.filter(c_user=user).update(c_tot_score=score)
            Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)
            score_context = {'score': score, 'cat_dict': cat_dict, 'total_q_asked': total_q_asked - 1,
                             'total_q_ans_correct': total_q_ans_correct}
            return render(request, 'AIP/report.html', score_context)

        counter += 1
        request.session['score'] = score
        request.session['counter'] = counter
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        request.session['cat_dict'] = cat_dict

        questions = Question.objects.filter(q_subject=subject, q_rank=rank)
        max = Question.objects.filter(q_subject=subject, q_rank=rank).count()
        ind = random.randint(1, max)
        question = questions[ind]
        context = {'total_q_asked': total_q_asked, 'question': question}
        return render(request, 'AIP/quizsimple.html', context)
    else:
        # this is GET flow of 1st question
        return render(request, 'AIP/quizsimple.html', context)


def quiz(request):
    subject = request.session['skill']
    rank = request.session['proficiency']
    curr_difficulty_score = request.session['curr_difficulty_score']
    total_q_asked = request.session['total_q_asked']
    total_q_ans_correct = request.session['total_q_ans_correct']
    score = request.session['score']
    cat_dict = request.session['cat_dict']
    user = request.session['user']
    counter = request.session['counter']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
    question = questions[0]
    context = {'total_q_asked': total_q_asked, 'question': question}

    if request.method == 'POST':
        option = request.POST.get('options')
        q = Question(question.pk)
        ans = Answer()
        ans.question = q
        question.no_times_ques_served += 1
        total_q_asked += 1
        if question.q_answer == option:
            ans.ans_option = option
            ans.is_correct = True
            question.no_times_anwered_correctly += 1
            total_q_ans_correct += 1
            cat_dict[question.q_cat] += 1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,
                                                no_times_anwered_correctly=question.no_times_anwered_correctly,
                                                no_times_anwered_incorrectly=question.no_times_anwered_incorrectly,
                                                difficulty_score=curr_difficulty_score)

        if counter == 20 or request.POST.get('END') == 'STOP':
            score1 = (total_q_ans_correct / (total_q_asked - 1)) * 100
            score = round(score1)
            cat_scores = json.dumps(cat_dict)
            Result.objects.filter(c_user=user).update(c_tot_score=score)
            Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)
            score_context = {'score': score, 'cat_dict': cat_dict, 'total_q_asked': total_q_asked - 1,
                             'total_q_ans_correct': total_q_ans_correct}
            return render(request, 'AIP/report.html', score_context)

        counter += 1
        request.session['counter'] = counter
        request.session['score'] = score
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        request.session['curr_difficulty_score'] = curr_difficulty_score
        request.session['cat_dict'] = cat_dict

        # curr_difficulty_score = question.no_times_anwered_incorrectly / question.no_times_anwered_incorrectly + question.no_times_anwered_correctly
        curr_difficulty_score = question.no_times_anwered_incorrectly / question.no_times_ques_served
        questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(
            difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
        question = questions[0]
        context = {'total_q_asked': total_q_asked, 'question': question}
        return render(request, 'AIP/quiz.html', context)
    else:
        return render(request, 'AIP/quiz.html', context)


def comment(request):
    context = {}
    user = request.session['user']
    if request.method == 'POST':
        comment = request.POST.get('comment')
        Result.objects.filter(c_user=user).update(c_comment=comment)
        context['commsuccess'] = "Comment added . Thank You !"
        return render(request, 'AIP/report.html', context)


def question(request):
    context = {}
    user = request.session['user']
    if request.method == 'POST':
        question = request.POST.get('question')
        Result.objects.filter(c_user=user).update(c_new_quest=question)
        context['quessuccess'] = "Question added . Thank You !"
        return render(request, 'AIP/report.html', context)


def upload(request):
    context = {}
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['document']
        except MultiValueDictKeyError:
            return HttpResponse("Please upload a file")

        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'AIP/report.html', context)


def logout(request):
    try:
        del request.session['user']
    except KeyError:
        pass

    return render(request, 'AIP/index.html')


def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(
        ['q_subject', 'q_cat', 'q_rank', 'q_text', 'q_option1', 'q_option2', 'q_option3', 'q_option4', 'q_answer',
         'q_ask_time', 'no_times_ques_served', 'no_times_anwered_correctly', 'no_times_anwered_incorrectly',
         'difficulty_score'])
    for data in Question.objects.all().values_list('q_subject', 'q_cat', 'q_rank', 'q_text', 'q_option1', 'q_option2',
                                                   'q_option3', 'q_option4', 'q_answer', 'q_ask_time',
                                                   'no_times_ques_served', 'no_times_anwered_correctly',
                                                   'no_times_anwered_incorrectly', 'difficulty_score'):
        writer.writerow(data)

    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    return response


@permission_required('admin.can_add_log_entry')
def debug(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(
        ['q_subject', 'q_cat', 'q_rank', 'q_text', 'q_option1', 'q_option2', 'q_option3', 'q_option4', 'q_answer',
         'q_ask_time', 'no_times_ques_served', 'no_times_anwered_correctly', 'no_times_anwered_incorrectly',
         'difficulty_score'])
    for data in Question.objects.all().values_list('q_subject', 'q_cat', 'q_rank', 'q_text', 'q_option1', 'q_option2',
                                                   'q_option3', 'q_option4', 'q_answer', 'q_ask_time',
                                                   'no_times_ques_served', 'no_times_anwered_correctly',
                                                   'no_times_anwered_incorrectly', 'difficulty_score'):
        writer.writerow(data)

    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    return response




@permission_required('admin.can_add_log_entry')
def questionupload(request):
    # template = question_upload.html

    prompt = {
        'order': 'Order of CSV should be Question,Option1,Option2,Option3,Option4,answer option'
    }
    if request.method == "GET":
        return render(request, 'AIP/question_upload.html', prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a cvs file')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter='|'):
        _, created = Question.objects.update_or_create(
            q_subject=column[0],
            q_cat=column[1],
            q_rank=column[2],
            q_text=column[3],
            q_option1=column[4],
            q_option2=column[5],
            q_option3=column[6],
            q_option4=column[7],
            q_answer=column[8]
        )
        context = {}
    return render(request, 'AIP/question_upload.html', context)


@permission_required('admin.can_add_log_entry')
def scores(request):
    results = Result.objects.all().order_by('-c_attempt_date')
    context = {'results': results}
    return render(request, 'AIP/scores.html', context)

@permission_required('admin.can_add_log_entry')
def quizzes(request):
    quizzes = list(Quiz.objects.all())
    context = {'quizzes': quizzes}
    return render(request, 'AIP/quizzes.html',context)

def addquiz(request):
    return  render(request, 'AIP/quizadd.html')

def  addquestion(request):
    subject = request.POST['Subject']
    category = request.POST['Category']
    request.session['subject'] = subject
    request.session['category'] = category
    request.session['questionlist'] = []
    request.session['count'] = 1
    request.session['countdrop'] = 1
    questions = list(Question.objects.all())
    context = {'subject': subject, 'category': category, 'questions': questions}
    return render(request, 'AIP/addquestion.html', context)


def add(request):
    #return  HttpResponse(request.method)
    subject = request.session['subject']
    category = request.session['category']
    count = request.session['count']
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            question.save()

            if count == 2:
                #quizzes = Quiz.objects.all()
                context = {'subject': subject,'category':category}
                return render(request, 'AIP/quizzes.html', context)

        count += 1
        request.session['count'] = count
        form = QuestionForm()
        return render(request, 'AIP/add.html',  {'form': form})
        #return redirect('AIP:index')
    else:
        form = QuestionForm()
        return render(request, 'AIP/add.html', {'form': form})


def addquestion1(request):
    subject          = request.session['subject']
    category         = request.session['category']
    questionlist     = request.session['questionlist']
    countdrop        = request.session['countdrop']

    questions = list(Question.objects.all())
    context = {'questions': questions}
    if request.method == 'POST':
        selectedquestion = request.POST.get('drop1')
        questionlist.append(selectedquestion)

        if countdrop == 20 or request.POST.get('END') == 'STOP':
            q = Quiz()
            q.quiz_name = subject
            q.quiz_subject = category
            q.quiz_questions = json.dumps(questionlist)
            q.quiz_noofquest = countdrop
            q.save()
            quizzes = Quiz.objects.all()
            context = {'quizzes': quizzes}
            return render(request, 'AIP/quizzes.html',context)

        countdrop += 1
        request.session['countdrop'] = countdrop
        return render(request, 'AIP/addquestion1.html', context)
    else:
        #return HttpResponse(request.method)
        return render(request, 'AIP/addquestion1.html', context)

def quizbucket(request):
    return  render(request, 'AIP/quizbucket.html')