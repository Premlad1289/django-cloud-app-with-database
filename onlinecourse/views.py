from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .models import Course, Lesson, Enrollment, Question, Choice, Submission


def popular_course_list(request):
    context = {}
    if request.method == 'GET':
        course_list = Course.objects.order_by('-total_enrollment')[:10]
        context['course_list'] = course_list
        return render(request, 'onlinecourse/course_list.html', context)


def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        if not user.is_authenticated:
            return redirect("onlinecourse:login")
        Enrollment.objects.create(user=user, course=course, mode='audit')
        course.total_enrollment += 1
        course.save()
        return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def course_details(request, course_id):
    context = {}
    if request.method == 'GET':
        course = get_object_or_404(Course, pk=course_id)
        context['course'] = course
        return render(request, 'onlinecourse/course_details_bootstrap.html', context)


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    selected_choice_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_choice_ids.append(int(value))
            
    for choice_id in selected_choice_ids:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)
        
    submission.save()
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_ids = [choice.id for choice in submission.choices.all()]
    total_score = 0
    questions = course.question_set.all()
    
    for question in questions:
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    context['course'] = course
    context['grade'] = total_score
    context['choices'] = selected_ids
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
