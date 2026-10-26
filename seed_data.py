"""
Standalone seed script for the IBM Coursera Django Cloud App project.
Automatically:
1. Runs makemigrations and migrate.
2. Creates superuser (admin / admin123).
3. Populates sample Course, Lessons, Questions, and Choices.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils.timezone import now
from onlinecourse.models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment, Submission


def run_seed():
    print("Step 1: Running makemigrations and migrate...")
    call_command('makemigrations', 'onlinecourse')
    call_command('migrate')

    print("Step 2: Creating superuser (admin)...")
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    instructor, _ = Instructor.objects.get_or_create(user=admin_user, defaults={'total_learners': 150})

    print("Step 3: Creating sample Course and Lessons...")
    course, _ = Course.objects.get_or_create(
        name="Cloud Application Development with Django",
        defaults={
            'description': "Learn how to build, deploy, and scale robust cloud-native web applications using Python, Django, and cloud database services.",
            'pub_date': now().date(),
            'total_enrollment': 25,
        }
    )
    course.instructors.add(instructor)
    course.save()

    course.lesson_set.all().delete()
    course.question_set.all().delete()

    Lesson.objects.create(
        title="Introduction to Cloud Computing & Django Architecture",
        order=0,
        course=course,
        content=(
            "Cloud computing delivers computing services over the internet. Django is a high-level Python web framework "
            "designed for rapid and clean development following the Model-View-Template (MVT) pattern."
        )
    )

    Lesson.objects.create(
        title="Developing Models, Views, and Database Migrations",
        order=1,
        course=course,
        content=(
            "Django's Object-Relational Mapper (ORM) allows developers to interact with database tables using Python code. "
            "Migrations safely propagate model changes into SQLite, PostgreSQL, or cloud databases."
        )
    )

    print("Step 4: Creating Questions and Choices...")
    q1 = Question.objects.create(
        course=course,
        question_text="Which architectural pattern does Django follow to structure web applications?",
        grade=50
    )
    Choice.objects.create(question=q1, choice_text="Model-View-Template (MVT)", is_correct=True)
    Choice.objects.create(question=q1, choice_text="Model-View-Presenter (MVP)", is_correct=False)
    Choice.objects.create(question=q1, choice_text="Single Page Application (SPA)", is_correct=False)
    Choice.objects.create(question=q1, choice_text="Client-Server Direct Database Querying", is_correct=False)

    q2 = Question.objects.create(
        course=course,
        question_text="Which Django management command applies pending database migrations to the configured database?",
        grade=50
    )
    Choice.objects.create(question=q2, choice_text="python manage.py migrate", is_correct=True)
    Choice.objects.create(question=q2, choice_text="python manage.py runserver", is_correct=False)
    Choice.objects.create(question=q2, choice_text="python manage.py startapp", is_correct=False)
    Choice.objects.create(question=q2, choice_text="python manage.py inspectdb", is_correct=False)

    student, _ = User.objects.get_or_create(
        username='student',
        defaults={'email': 'student@example.com', 'first_name': 'Jane', 'last_name': 'Doe'}
    )
    student.set_password('student123')
    student.save()
    Learner.objects.get_or_create(user=student, defaults={'occupation': Learner.DEVELOPER, 'social_link': 'https://github.com/'})
    en, _ = Enrollment.objects.get_or_create(user=student, course=course, defaults={'mode': 'honor'})

    sub, _ = Submission.objects.get_or_create(enrollment=en)
    sub.choices.clear()
    for q in course.question_set.all():
        for ch in q.choice_set.filter(is_correct=True):
            sub.choices.add(ch)
    sub.save()

    print("Database seeded successfully with course, questions, choices, and passing submission!")


if __name__ == '__main__':
    run_seed()
