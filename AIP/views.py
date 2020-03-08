import datetime

from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage

from .forms import TakeQuizForm

# Create your views here.
from .models import Question,Answer,Result
from django.http import HttpResponse
import json
import  random


def index(request):
    return render(request, 'AIP/index.html')

def pickskill(request):
    request.session['user'] = request.user.get_username()
    user = request.session['user']
    Result.objects.create(c_user = user)
    return  render(request, 'AIP/pickskill.html')

def begin(request):
    if request.method == 'POST':
        subject = request.POST['skill']
        rank = request.POST['proficiency']
        context = {'subject':subject,'rank':rank}

        request.session['skill'] = subject
        request.session['proficiency'] = rank
        request.session['curr_difficulty_score'] = 1
        request.session['total_q_asked'] = 1
        request.session['total_q_ans_correct'] = 0
        request.session['counter']  = 0
        cat_dict = {'Introduction': 0, 'Syntax': 0, 'OOPS': 0, 'NativeDataTypes': 0, 'FileAndExceptionHandling': 0,
                    'Function': 0, 'Advanced': 0}
        request.session['cat_dict'] = cat_dict
        #request.session['counter'] = random.randint(1, 100)        # use this in production
        request.session['score'] = 0

        if rank == 'Adaptive':
            return render(request, 'AIP/begin.html',context)
        else:
            return render(request, 'AIP/beginsimple.html',context)

def displayformat(question):
    b = question
    a = b.split("|")

    out = []
    empty = "    "

    func_name  = ""
    func_name1 = ""
    func_name2 = ""
    for entry in a:
        if 'def' in entry:
            c = entry.split(" ")
            if "(" in c[1]:
                d = c[1].split("(")
                func_name = d[0]
                func_name1 = func_name + "("
                func_name2 = "print" + func_name1

    for entry in a:
        if 'def' in entry:
            out.append(entry)
        elif func_name1 in entry:
            out.append(entry)
        elif func_name2 in entry:
            out.append(entry)
        else:
            newdata = empty + entry
            out.append(newdata)

    return out

def quizsimple(request):
    subject                  = request.session['skill']
    rank                     = request.session['proficiency']
    total_q_asked            = request.session['total_q_asked']
    total_q_ans_correct      = request.session['total_q_ans_correct']
    counter                  = request.session['counter']
    score                    = request.session['score']
    cat_dict                 = request.session['cat_dict']
    user                     = request.session['user']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank)
    cat_scores = json.dumps(cat_dict)
    Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)
    score_context = {'score':score,'cat_dict':cat_dict}
    #return HttpResponse(cat_dict)

    if questions.count() == 0 or total_q_asked == 6:
        #return render(request, 'AIP/report.html',{'score':score})
        return render(request, 'AIP/report.html', score_context)

    total_questions = questions.count()
    question = questions[counter]
    out = []
    if '|' in question.q_text :
        out = displayformat(question.q_text)

    if len(out) == 0:
        context = {'total_q_asked': total_q_asked, 'question': question}
    else:
        context = {'total_q_asked': total_q_asked, 'question': question, 'out': out}

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
            cat_dict[question.q_cat] += 1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,no_times_anwered_correctly=question.no_times_anwered_correctly,no_times_anwered_incorrectly=question.no_times_anwered_incorrectly)
        score = (total_q_ans_correct / (total_q_asked )) * 100
        cat_scores = json.dumps(cat_dict)
        #return HttpResponse(cat_scores)

        Result.objects.filter(c_user=user).update(c_tot_score=score)
        Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)

        questions = Question.objects.filter(q_subject=subject, q_rank=rank)
        score_context = {'score': score, 'cat_dict': cat_dict}

        if questions.count() ==0 or total_q_asked == 6:
            #return HttpResponse(cat_dict)
            #return render(request, 'AIP/report.html',{'score':score})
            return render(request, 'AIP/report.html',score_context)

        counter += 1
        total_q_asked += 1
        question = questions[counter]
        out = []
        if '|' in question.q_text:
            out = displayformat(question.q_text)

        if len(out) == 0:
            context = {'total_q_asked': total_q_asked, 'question': question}
        else:
            context = {'total_q_asked': total_q_asked, 'question': question, 'out': out}

        request.session['score'] = score
        request.session['counter'] = counter
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        request.session['cat_dict'] = cat_dict
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
    cat_dict                 = request.session['cat_dict']
    user                     = request.session['user']

    questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
    cat_scores = json.dumps(cat_dict)
    Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)

    if questions.count() == 0:
        return render(request, 'AIP/report.html',{'score':score})

    total_questions = questions.count()
    question = questions[0]
    out = []
    if '|' in question.q_text :
        out = displayformat(question.q_text)

    if len(out) == 0:
        context = {'total_q_asked': total_q_asked, 'question': question}
    else:
        context = {'total_q_asked': total_q_asked, 'question': question, 'out': out}

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
            cat_dict[question.q_cat] += 1
            ans.save()
        else:
            ans.ans_option = option
            ans.is_correct = False
            question.no_times_anwered_incorrectly += 1
            ans.save()

        Question.objects.filter(pk=q.pk).update(no_times_ques_served=question.no_times_ques_served,no_times_anwered_correctly=question.no_times_anwered_correctly,no_times_anwered_incorrectly=question.no_times_anwered_incorrectly,difficulty_score=curr_difficulty_score)
        score = (total_q_ans_correct / total_q_asked) * 100
        cat_scores = json.dumps(cat_dict)

        Result.objects.filter(c_user=user).update(c_tot_score=score)
        Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)
        #curr_difficulty_score = question.no_times_anwered_incorrectly / question.no_times_anwered_incorrectly + question.no_times_anwered_correctly

        curr_difficulty_score = question.no_times_anwered_incorrectly / question.no_times_ques_served
        questions = Question.objects.filter(q_subject=subject, q_rank=rank).filter(difficulty_score__gt=curr_difficulty_score).order_by('difficulty_score')
        if questions.count() == 0:
            return render(request, 'AIP/report.html' ,{'score':score})

        total_q_asked += 1
        question = questions[0]
        out = []
        if '|' in question.q_text:
            out = displayformat(question.q_text)

        if len(out) == 0:
            context = {'total_q_asked': total_q_asked, 'question': question}
        else:
            context = {'total_q_asked': total_q_asked, 'question': question, 'out': out}

        request.session['score'] = score
        request.session['total_q_asked'] = total_q_asked
        request.session['total_q_ans_correct'] = total_q_ans_correct
        request.session['curr_difficulty_score'] = curr_difficulty_score
        request.session['cat_dict'] = cat_dict
        return render(request, 'AIP/quiz.html',context)
    else:
        return render(request, 'AIP/quiz.html',context)

def report(request):
    score = request.session['score']
    cat_dict = request.session['cat_dict']
    score_context = {'score': score, 'cat_dict': cat_dict}
    return render(request, 'AIP/report.html',score_context)

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
        question      = request.POST.get('question')
        Result.objects.filter(c_user=user).update(c_new_quest=question)
        context['quessuccess'] = "Question added . Thank You !"
        return render(request, 'AIP/report.html', context)


def upload(request):
    context   = {}
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['document']
        except MultiValueDictKeyError :
            return  HttpResponse("Please upload a file")

        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name,uploaded_file)
        context['url'] = fs.url(name)
    return  render(request,'AIP/report.html',context)

def logout(request):
    try:
        del request.session['user']
    except KeyError:
        pass

    return render(request, 'AIP/index.html')
