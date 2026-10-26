from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
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
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course, defaults={'mode': 'audit'})
        if created:
            course.total_enrollment += 1
            course.save()
        return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))
    return redirect('onlinecourse:course_details', course_id=course_id)


def course_details(request, course_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    context['course'] = course
    context['is_enrolled'] = is_enrolled
    return render(request, 'onlinecourse/course_details_bootstrap.html', context)


def submit(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        if not user.is_authenticated:
            return redirect('onlinecourse:login')

        enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course, defaults={'mode': 'audit'})
        submission = Submission.objects.create(enrollment=enrollment)

        selected_choice_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                try:
                    selected_choice_ids.append(int(value))
                except ValueError:
                    pass

        for choice_id in selected_choice_ids:
            choice = get_object_or_404(Choice, pk=choice_id)
            submission.choices.add(choice)

        submission.save()
        return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))
    return redirect('onlinecourse:course_details', course_id=course_id)


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_ids = list(submission.choices.values_list('id', flat=True))
    total_score = 0
    possible_score = 0
    questions = course.question_set.all()

    for question in questions:
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['possible'] = possible_score
    context['possible_score'] = possible_score
    context['selected_ids'] = selected_ids
    context['choices'] = selected_ids
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw') or request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/login.html', context)
    return render(request, 'onlinecourse/login.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def registration_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw') or request.POST.get('password')
        first_name = request.POST.get('firstname', '')
        last_name = request.POST.get('lastname', '')
        if User.objects.filter(username=username).exists():
            context['message'] = "Username already exists. Please choose a different username."
            return render(request, 'onlinecourse/registration.html', context)
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        return redirect('onlinecourse:index')
    return render(request, 'onlinecourse/registration.html', context)
