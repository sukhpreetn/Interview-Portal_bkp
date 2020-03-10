import datetime

from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from .models import Question,Answer,Result
from django.http import HttpResponse
import json
import  random
import csv , io

from django.contrib import messages
from django.contrib.auth.decorators import  permission_required
from .forms import QuestionForm


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

    if questions.count() == 0 or total_q_asked == 4:
        #return render(request, 'AIP/report.html',{'score':score})
        return render(request, 'AIP/report.html', score_context)

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

        Result.objects.filter(c_user=user).update(c_tot_score=score)
        Result.objects.filter(c_user=user).update(c_cat_scores=cat_scores)

        questions = Question.objects.filter(q_subject=subject, q_rank=rank)
        score_context = {'score': score, 'cat_dict': cat_dict}

        if questions.count() ==0 or total_q_asked == 4:
            return render(request, 'AIP/report.html',score_context)

        counter += 1
        total_q_asked += 1
        question = questions[counter]
        context = {'total_q_asked': total_q_asked, 'question': question}

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
    score_context = {'score': score, 'cat_dict': cat_dict}

    if questions.count() == 0:
        return render(request, 'AIP/report.html',score_context)

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
        score_context = {'score': score, 'cat_dict': cat_dict}
        if questions.count() == 0:
            return render(request, 'AIP/report.html' ,score_context)

        total_q_asked += 1
        question = questions[0]
        context = {'total_q_asked': total_q_asked, 'question': question}
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

def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['q_subject','q_cat','q_rank','q_text','q_option1','q_option2','q_option3','q_option4','q_answer','q_ask_time','no_times_ques_served','no_times_anwered_correctly','no_times_anwered_incorrectly','difficulty_score'])
    for data in Question.objects.all().values_list('q_subject','q_cat','q_rank','q_text','q_option1','q_option2','q_option3','q_option4','q_answer','q_ask_time','no_times_ques_served','no_times_anwered_correctly','no_times_anwered_incorrectly','difficulty_score'):
        writer.writerow(data)

    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    return response

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

def add(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            question.save()
        return redirect('AIP:index')
    else:
        form = QuestionForm()
    return render(request, 'AIP/add.html', {'form': form})

@permission_required('admin.can_add_log_entry')
def questionupload(request):
    #template = question_upload.html

    prompt  = {
        'order': 'Order of CSV should be Question,Option1,Option2,Option3,Option4,answer option'
    }
    if request.method == "GET":
        return  render(request,'AIP/question_upload.html',prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request,'This is not a cvs file')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string,delimiter = ',',quotechar = "|"):
        _,created = Question.objects.update_or_create(
            q_text = column[0],
            q_option1 = column[1],
            q_option2 = column[2],
            q_option3 = column[3],
            q_option4 = column[4],
            q_answer = column[5]
        )
        context = {}
    return render(request, 'AIP/question_upload.html',context)


