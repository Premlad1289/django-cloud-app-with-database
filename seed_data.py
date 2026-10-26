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

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils.timezone import now
from onlinecourse.models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment


def run_seed():
    print("Step 1: Running makemigrations and migrate...")
    call_command('makemigrations', 'onlinecourse')
    call_command('migrate')

    print("Step 2: Creating superuser (admin)...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    if created:
        print("  Superuser 'admin' created successfully with password 'admin123'.")
    else:
        print("  Superuser 'admin' updated successfully with password 'admin123'.")

    # Create instructor
    instructor, _ = Instructor.objects.get_or_create(
        user=admin_user,
        defaults={'total_learners': 150}
    )

    print("Step 3: Creating sample Course and Lessons...")
    course, course_created = Course.objects.get_or_create(
        name="Cloud Application Development with Django",
        defaults={
            'description': "Learn how to build, deploy, and scale robust cloud-native web applications using Python, Django, and cloud database services.",
            'pub_date': now().date(),
            'total_enrollment': 25,
        }
    )
    course.instructors.add(instructor)
    course.save()

    # Clear old lessons and questions for clean idempotency if re-run
    course.lesson_set.all().delete()
    course.question_set.all().delete()

    Lesson.objects.create(
        title="Introduction to Cloud Computing & Django Architecture",
        order=0,
        course=course,
        content=(
            "Cloud computing delivers computing services—including servers, storage, databases, networking, and software—over the internet. "
            "Django is a high-level Python web framework designed for rapid and clean development. It follows the Model-View-Template (MVT) "
            "architectural pattern to separate database schema, application logic, and user presentation."
        )
    )

    Lesson.objects.create(
        title="Developing Models, Views, and Database Migrations",
        order=1,
        course=course,
        content=(
            "Django's Object-Relational Mapper (ORM) allows developers to interact with database tables using Python code. "
            "Using 'python manage.py makemigrations' and 'python manage.py migrate', changes to models are safely and seamlessly "
            "applied to SQLite, PostgreSQL, or cloud-hosted database instances."
        )
    )

    print("Step 4: Creating Questions and Choices...")
    # Question 1
    q1 = Question.objects.create(
        question_text="Which architectural pattern does Django follow to structure web applications?",
        grade=50
    )
    q1.courses.add(course)

    Choice.objects.create(question=q1, choice_text="Model-View-Template (MVT)", is_correct=True)
    Choice.objects.create(question=q1, choice_text="Model-View-Presenter (MVP)", is_correct=False)
    Choice.objects.create(question=q1, choice_text="Single Page Application (SPA)", is_correct=False)
    Choice.objects.create(question=q1, choice_text="Client-Server Direct Database Querying", is_correct=False)

    # Question 2
    q2 = Question.objects.create(
        question_text="Which Django management command applies pending database migrations to the configured database?",
        grade=50
    )
    q2.courses.add(course)

    Choice.objects.create(question=q2, choice_text="python manage.py migrate", is_correct=True)
    Choice.objects.create(question=q2, choice_text="python manage.py runserver", is_correct=False)
    Choice.objects.create(question=q2, choice_text="python manage.py startapp", is_correct=False)
    Choice.objects.create(question=q2, choice_text="python manage.py inspectdb", is_correct=False)

    # Create a test learner user
    student, s_created = User.objects.get_or_create(
        username='student',
        defaults={'email': 'student@example.com', 'first_name': 'Jane', 'last_name': 'Doe'}
    )
    student.set_password('student123')
    student.save()
    Learner.objects.get_or_create(
        user=student,
        defaults={'occupation': Learner.DEVELOPER, 'social_link': 'https://github.com/'}
    )
    Enrollment.objects.get_or_create(user=student, course=course, defaults={'mode': 'honor'})

    print("\nDatabase seeded successfully!")
    print("--------------------------------------------------")
    print("Superuser:  username: admin   | password: admin123")
    print("Test User:  username: student | password: student123")
    print("Sample Course: 'Cloud Application Development with Django'")
    print("Two sample questions (50 pts each) with choices populated.")
    print("--------------------------------------------------")


if __name__ == '__main__':
    run_seed()
