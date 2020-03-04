import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError

from .forms import TakeQuizForm

# Create your views here.
from .models import Question,Answer, Comment
from django.http import HttpResponse
import json

def index(request):
    return render(request, 'AIP/index.html')

def pickskill(request):
    return  render(request, 'AIP/pickskill.html')

def begin(request):
    if request.method == 'POST':
        subject = request.POST['skill']
        rank = request.POST['proficiency']
        context = {'subject':subject,'rank':rank}
        request.session['firstflag'] = False           
        return render(request, 'AIP/begin.html',context)

    

def quiz1():
    questions = Question.objects.filter(q_subject=subject,q_rank=rank)
    total_questions = questions.count()


    return HttpResponse("hey")
    #request.session['difficulty_score'] = questions[0].difficulty_score
    #return HttpResponse(request.method )

    if request.method == 'POST':
        #return HttpResponse("hey")
        form = TakeQuizForm(question=question, data=request.POST)
        #return HttpResponse("hey")
        if form.is_valid():
            #return HttpResponse("valid")
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return HttpResponse("pk")
                    return redirect('students:take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('students:quiz_list')
    else:
        return HttpResponse("hello")
        form = TakeQuizForm(question=question)
        #return HttpResponse(form)

    return render(request, 'AIP/index.html')
    #context = {'question': questions[0],'total_questions':total_questions}
    #return render(request, 'AIP/quiz.html', context)


def quiz2(request):
    if request.method == 'POST':
        #return  HttpResponse("hey")
        form = TakeQuizForm(request.POST)
        if form.is_valid():
           return  HttpResponse("hello")
           author = form.save()
           author.save()
           return redirect('AIP:index')
    else:
        #return  HttpResponse("empty")
        form = TakeQuizForm()
    return render(request, 'AIP/quiz.html', {'form': form})


'''
    flag  = request.session['firstflag']
    if flag == False:
        #return HttpResponse("1")

        questions = Question.objects.filter(q_subject=subject,q_rank=rank)
        total_questions = questions.count()
        request.session['difficulty_score'] = questions[0].difficulty_score

        context = {'question': questions[0],'total_questions':total_questions}
        return render(request, 'AIP/quiz.html', context)

        request.session['firstflag'] = True
    else:
        return HttpResponse("2")
        return redirect('students:index', subject,rank)

        request.session['firstflag'] = True
          '''

''' 
    if request.method == 'POST':
        option = request.POST.get('options')
        return HttpResponse(option)
      
        #if answer == questions[0].ans_text:


        form = TakeQuizForm(data=request.POST,instance=questions[0])
        #return HttpResponse(form)
        if form.is_valid():
            return HttpResponse("valid")
            q = form.save()
            q.save()
            request.session['answered'] = quest_no + 1
            return redirect('index')
            '''
'''
            if list it not empty
                return redirect('AIP:quiz')
            else:
                calculate scores
                redirect to result
            '''
'''
    else:
        return HttpResponse("invalid")
        form = TakeQuizForm(instance-question)
        return ("bye")
    #return render(request, 'AIP/quiz.html', {'form': form})
    return render(request, 'AIP/quiz.html', {'question': questions[0]})
'''

def next(request,pk):

    if request.method == 'POST':
        option = request.POST.get('options')

        ans = Answer()
        ans.question = Question(pk)
        return HttpResponse(Question(pk))
        ans.ans_option = option
        ans.is_correct = True

        ans.save()
        return render(request, 'AIP/next.html')

def report(request):
    return  render(request, 'AIP/report.html')


def takequiz(request):
    return  render(request, 'AIP/take_qui   z_form.html')


def start(request):
    if request.method == 'POST':
        subject = request.POST['skill']
        rank = request.POST['proficiency']
        context = {'subject':subject,'rank':rank}
        request.session['firstflag'] = False
        return render(request, 'AIP/start.html',context)