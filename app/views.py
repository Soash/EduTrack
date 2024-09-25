import json
import random, string
from datetime import datetime
from .forms import CustomPasswordChangeForm, ExamForm, LectureForm, NoteForm, NoticeForm, PeriodForm, SubjectForm
from .forms import StudentForm, TeacherForm, TeacherProfileForm, LectureForm, ResultForm, ResultFormSet
from .models import AttendanceRecord, CustomUser, Exam, Lectures, MonthlySalary, Notes, Notice, Period, Result, Routine, StudentClass, Subject, Teacher, Student, Lectures
from .serializers import AttendanceRecordSerializer, CustomUserSerializer, LecturesSerializer, MonthlySalarySerializer, NotesSerializer, RoutineSerializer 
from .serializers import NoticeSerializer, ResultSerializer, StudentCreateSerializer, TeacherSerializer, StudentSerializer

from django.db import transaction
from django.utils import timezone
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

 


class TeacherListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherSerializer
    queryset = Teacher.objects.all().order_by('-id')

class NoticeListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NoticeSerializer
    queryset = Notice.objects.all().order_by('-date')

class NotesListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NotesSerializer

    def get_queryset(self):
        if not self.request.user.is_student:
            return Notes.objects.none()
        return Notes.objects.filter(grade=self.request.user.student.grade).order_by('-date')

class LecturesListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LecturesSerializer

    def get_queryset(self):
        if not self.request.user.is_student:
            return Lectures.objects.none()  # Prevent non-students from viewing lectures
        # Filter lectures by the student's grade
        return Lectures.objects.filter(grade=self.request.user.student.grade).order_by('-date')
    
class RoutinesForWeekView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RoutineSerializer

    def get(self, request, *args, **kwargs):
        # Only allow students to access the routines
        if not request.user.is_student:
            return Response({"error": "Not authorized"}, status=403)

        # Get the student's grade
        grade = request.user.student.grade
        routines = Routine.objects.filter(grade=grade)

        # Prepare a dictionary to organize routines by day
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        routines_by_day = {day: [] for day in days}

        # Group routines by day
        for routine in routines:
            if routine.day in routines_by_day:
                routines_by_day[routine.day].append(RoutineSerializer(routine).data)

        return Response(routines_by_day)
    
class StudentInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = Student.objects.get(user=request.user)
        if student:
            serializer = StudentSerializer(student, context={'request': request})
            return Response(serializer.data)
        return Response({"error": "Student not found"}, status=404)

class StudentResultView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            student = Student.objects.get(user=user)
            results = Result.objects.filter(student=student)
            serializer = ResultSerializer(results, many=True, context={'request': request})
            return Response(serializer.data)

        except Student.DoesNotExist:
            return Response({"error": "Student not found for the logged-in user"}, status=404)
        except Result.DoesNotExist:
            return Response({"error": "Results not found for this student"}, status=404)

class StudentAttendanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the logged-in user
            user = request.user

            # Get the Student object associated with the logged-in user
            student = Student.objects.get(user=user)

            # Fetch the attendance records for the student
            attendance_records = AttendanceRecord.objects.filter(student=student).order_by('-date')

            # Serialize the attendance records
            serializer = AttendanceRecordSerializer(attendance_records, many=True, context={'request': request})

            return Response(serializer.data)

        except Student.DoesNotExist:
            return Response({"error": "Student not found for the logged-in user"}, status=404)
        
class StudentSalaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the logged-in user
            user = request.user

            # Get the Student object associated with the logged-in user
            student = Student.objects.get(user=user)

            # Fetch the attendance records for the student
            attendance_records = MonthlySalary.objects.filter(student=student).order_by('-date')

            # Serialize the attendance records
            serializer = MonthlySalarySerializer(attendance_records, many=True, context={'request': request})

            return Response(serializer.data)

        except Student.DoesNotExist:
            return Response({"error": "Student not found for the logged-in user"}, status=404)

############################################################################################################
############################################################################################################
############################################################################################################


def teacher_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse("You are not authorized to access this page.")
    else:
        form = AuthenticationForm()
    return render(request, 'teacher_login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('teacher_login')

@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def home(request):
    teacher = Teacher.objects.get(user=request.user)
    if request.method == 'POST':
        profile_form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if profile_form.is_valid():
            profile_form.save()
            return redirect('home')
        elif password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('home')
    else:
        profile_form = TeacherProfileForm(instance=teacher)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'home.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'teacher': teacher,
    })


############################################################################################################
# Attendance

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def attendance_record(request):
    if request.method == 'POST':
        grade = request.POST.get('grade')
        date = request.POST.get('date')

        if grade and date:
            students = Student.objects.filter(grade=grade)
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()

            # Get existing attendance records for the selected date
            existing_records = AttendanceRecord.objects.filter(date=attendance_date)

            # Create attendance records for students if they don't have one for the selected date
            for student in students:
                if not existing_records.filter(student=student).exists():
                    AttendanceRecord.objects.create(
                        student=student,
                        date=attendance_date,
                        status='present'  # Default status is absent
                    )

            # Fetch all attendance records for the date to show in the template
            attendance_records = AttendanceRecord.objects.filter(date=attendance_date)
            attendance_status = {record.student.id: record.status for record in attendance_records}

            date_str = str(attendance_date)
            return render(request, 'attendance_record.html', {
                'students': students,
                'attendance_date': attendance_date,
                'grade': grade,
                'date_str': date_str,
                'attendance_status': attendance_status
            })

    return render(request, 'attendance_filter.html')

@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def mark_attendance(request, status, id):
    if request.method == 'POST':
        status = request.POST.get('status')
        date = request.POST.get('date')
        date = datetime.strptime(date, '%Y-%m-%d').date()        
        student = get_object_or_404(Student, id=id)

        AttendanceRecord.objects.update_or_create(
            student=student,
            date=date,
            defaults={'status': status}
        )
        return JsonResponse({'success': True, 'status': status})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# Attendance
############################################################################################################

############################################################################################################
# Lecture

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def manage_lecture(request):
    lectures = Lectures.objects.all()
    if request.method == 'POST':
        form = LectureForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.added_by = request.user
            data.save()
            return redirect('manage_lecture')
    else:
        form = LectureForm()

    return render(request, 'manage_lecture.html', {'form': form, 'lectures': lectures})

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def delete_lecture(request, id):
    if request.method == 'POST':
        lecture = get_object_or_404(Lectures, id=id)
        lecture.delete()
        return redirect('add_lecture')

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
@require_POST
def update_lecture(request):
    """Update lecture data via AJAX."""
    lecture_id = request.POST.get('lecture_id')
    grade = request.POST.get('grade')
    subject = request.POST.get('subject')
    content = request.POST.get('content')
    url = request.POST.get('url')

    # Fetch the lecture object
    lecture = get_object_or_404(Lectures, id=lecture_id)

    # Update the lecture details
    lecture.grade = grade
    lecture.subject = subject
    lecture.content = content
    lecture.url = url
    lecture.save()

    # Return JSON response
    data = {
        'success': True,
        'lecture_id': lecture.id,
        'grade': lecture.grade,
        'subject': lecture.subject,
        'content': lecture.content,
        'url': lecture.url
    }
    return JsonResponse(data)

# Lecture
############################################################################################################

############################################################################################################
# Note

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def manage_note(request):
    notes = Notes.objects.all()
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.added_by = request.user
            data.save()
            return redirect('manage_note')
    else:
        form = NoteForm()

    return render(request, 'manage_note.html', {'form': form, 'notes': notes})

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def delete_note(request, id):
    if request.method == 'POST':
        note = get_object_or_404(Notes, id=id)
        note.delete()
        return redirect('manage_note')

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
@require_POST
def update_note(request):
    """Update note data via AJAX."""
    note_id = request.POST.get('note_id')
    grade = request.POST.get('grade')
    subject = request.POST.get('subject')
    content = request.POST.get('content')
    url = request.POST.get('url')
    pdf = request.FILES.get('pdf')

    # Fetch the note object
    note = get_object_or_404(Notes, id=note_id)

    # Update the note details
    note.grade = grade
    note.subject = subject
    note.content = content
    note.url = url
    if pdf:
        note.pdf = pdf
    note.save()

    # Return JSON response
    data = {
        'success': True,
        'note_id': note.id,
        'grade': note.grade,
        'subject': note.subject,
        'content': note.content,
        'url': note.url,
        'pdf': note.pdf.url if note.pdf else ''
    }
    return JsonResponse(data)

# Note
############################################################################################################

############################################################################################################
# Routine

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def manage_routine(request):
    # Fetch unique grades from the Routine model
    unique_grades = Routine.objects.values_list('grade', flat=True).distinct()

    if request.method == 'POST':
        grade = request.POST.get('grade')
        if grade:
            periods = Period.objects.all()
            for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']:
                for period in periods:
                    # Check if the routine for the grade, period, and day already exists
                    if not Routine.objects.filter(grade=grade, day=day, period=period).exists():
                        # If it doesn't exist, create a new routine
                        Routine.objects.create(
                            grade=grade,  # Store the grade as a string
                            day=day,
                            period=period
                        )
            return redirect('manage_routine')

    return render(request, 'manage_routine.html', {
        'unique_grades': unique_grades,
    })

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def view_routine(request, grade):
    periods = Period.objects.all()
    days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
    routines = Routine.objects.filter(grade=grade)

    routines_dict = {}
    for routine in routines:
        routines_dict[routine.id] = (routine.period.id, routine.day)

    context = {
        'grade': grade,
        'periods': periods,
        'days': days,
        'routines': routines_dict,
        'teachers': Teacher.objects.all(),
        'subjects': Subject.objects.all(),
    }

    return render(request, 'view_routine.html', context)

@login_required(login_url='teacher_login')
@require_POST
def update_routine(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            routine = get_object_or_404(Routine, id=id)

            teacher_id = data.get('teacher_id')
            subject_id = data.get('subject_id')

            if teacher_id:
                routine.teacher_id = teacher_id
            if subject_id:
                routine.subject_id = subject_id

            routine.save()
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            print(f"Error in update_routine: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def delete_routines(request, grade):
    if request.method == 'POST':
        Routine.objects.filter(grade=grade).delete()
        messages.success(request, f"All routines for Class {grade} have been deleted.")
        return redirect('manage_routine')
    
# Routine
############################################################################################################

############################################################################################################
# Notice

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def manage_notice(request):
    notices = Notice.objects.all()
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_notice')
    else:
        form = NoticeForm()

    return render(request, 'manage_notice.html', {'form': form, 'notices': notices})

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def delete_notice(request, id):
    if request.method == 'POST':
        notice = get_object_or_404(Notice, id=id)
        notice.delete()
        return redirect('manage_notice')

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
@require_POST
def update_notice(request):
    """Update routine data via AJAX."""
    notice_id = request.POST.get('notice_id')
    content = request.POST.get('content')

    # Fetch the routine object
    notice = get_object_or_404(Notice, id=notice_id)

    # Update the routine details
    notice.content = content
    notice.save()

    # Prepare data for the JSON response
    data = {
        'success': True,
        'notice_id': notice.id,
        'content': notice.content,
    }

    return JsonResponse(data)

# Notice
############################################################################################################

############################################################################################################
# Exam Result

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def update_exam_results(request, exam_id):
    # Get the exam by ID
    exam = get_object_or_404(Exam, id=exam_id)
    ResultFormSet = modelformset_factory(Result, form=ResultForm, extra=0)

    # Get all results associated with the exam
    results = Result.objects.filter(exam=exam)

    if request.method == 'POST':
        formset = ResultFormSet(request.POST, queryset=results)
        if formset.is_valid():
            # Save the formset data first
            formset.save()

            # Calculate positions based on exam_marks
            results = Result.objects.filter(exam=exam).order_by('-exam_marks')
            position = 1
            last_marks = None
            last_position = 1  # Start at 1, not 0

            for result in results:
                if result.exam_marks != last_marks:
                    # If the current marks are different from the last marks, update the position
                    result.position = position
                else:
                    # If the current marks are the same as the last marks, keep the same position
                    result.position = last_position
                
                # Save the result with the updated position
                result.save()
                
                # Update tracking variables
                last_marks = result.exam_marks
                last_position = result.position
                
                # Increment position for the next student
                position += 1

            return redirect('update_exam_results', exam_id=exam_id)
        else:
            # Print formset errors to debug why it's not valid
            print(formset.errors)
    else:
        # Populate the formset with data from the database
        formset = ResultFormSet(queryset=results)

    # Render the update exam results page with the formset
    return render(request, 'manage_exam_results.html', {
        'formset': formset,
        'exam': exam
    })

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def view_exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    results = Result.objects.filter(exam=exam)
    return render(request, 'manage_exam_results_view.html', {
        'results': results,
        'exam': exam
    })

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def manage_exam(request):
    exams = Exam.objects.all()
    if request.method == 'POST':
        form = ExamForm(request.POST, request.FILES)
        if form.is_valid():
            exam = form.save()
            students_in_grade = Student.objects.filter(grade=exam.grade)
                # Prepare bulk results creation
            results = [
                Result(exam=exam, student=student, exam_marks=0)
                for student in students_in_grade
            ]

            # Use a transaction to bulk create the results
            with transaction.atomic():
                Result.objects.bulk_create(results)
            return redirect('manage_exam')
    else:
        form = ExamForm()
    return render(request, 'manage_exam.html', {'exams': exams, 'form': form,})

@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def delete_exam(request, id):
    if request.method == 'POST':
        exam = get_object_or_404(Exam, id=id)
        exam.delete()
        return redirect('manage_exam')

@require_POST
@login_required(login_url='teacher_login')
@user_passes_test(lambda user: user.is_staff)
def update_exam(request):
    """Update exam data via AJAX."""
    id = request.POST.get('id')
    name = request.POST.get('name')
    subject = request.POST.get('subject')
    date = request.POST.get('date')
    total_marks = request.POST.get('total_marks')

    # Fetch the exam object
    data = get_object_or_404(Exam, id=id)

    # Update the exam details
    data.name = name
    data.subject = subject
    data.date = date
    data.total_marks = total_marks
    data.save()

    # Prepare data for the JSON response
    data = {
        'success': True,
        'id': data.id,
        'name': data.name,
        'subject': data.subject,
        'date': data.date,
        'total_marks': data.total_marks,
    }

    return JsonResponse(data)

# Exam Result
############################################################################################################

############################################################################################################
# Teacher

def generate_unique_username(base_username):
    # username = base_username.lower()
    username = base_username
    username = ''.join([char for char in username if char.isalpha()])

    # Check if the username exists
    if CustomUser.objects.filter(username=username).exists():
        # Append a random 4-digit number
        random_number = ''.join(random.choices(string.digits, k=4))
        username = f"{username}{random_number}"
    
    # Ensure the new username is unique
    while CustomUser.objects.filter(username=username).exists():
        random_number = ''.join(random.choices(string.digits, k=4))
        username = f"{base_username}{random_number}"
    
    return username

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def manage_teacher(request):
    teachers = Teacher.objects.all()

    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            base_username = form.cleaned_data['name']
            unique_username = generate_unique_username(base_username)

            # Create a new CustomUser for the teacher
            user = CustomUser.objects.create(
                username=unique_username,
                is_teacher=True,
                is_staff=True,
                is_superuser=form.cleaned_data['is_superuser'],
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            teacher = form.save(commit=False)
            teacher.user = user
            teacher.added_by = request.user
            teacher.save()
            return redirect('manage_teacher')
    else:
        form = TeacherForm()

    return render(request, 'manage_teacher.html', {'form': form, 'teachers': teachers})

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    teacher.delete()
    return redirect('manage_teacher')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def update_teacher(request):
    """Update teacher data via AJAX."""
    print('ok')
    teacher_id = request.POST.get('id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    # Update teacher details
    teacher.name = request.POST.get('name')
    teacher.phone = request.POST.get('phone')
    teacher.subject = request.POST.get('subject')

    new_password = request.POST.get('password')
    if new_password:
        teacher.user.set_password(new_password)
        teacher.user.save()
    is_superuser = request.POST.get('is_superuser') == 'true'
    teacher.user.is_superuser = is_superuser
    teacher.user.save()
    
    img = request.FILES.get('img')  # Handle file upload
    if img:
        teacher.img = img  # Update image if provided

    teacher.save()
    print('save')
    # Prepare data for the JSON response
    data = {
        'success': True,
        'id': teacher.id,
        'name': teacher.name,
        'phone': teacher.phone,
        'subject': teacher.subject,
        'img': teacher.img.url if teacher.img else ''  # Handle image URL in response
    }

    return JsonResponse(data)

# Teacher
############################################################################################################

############################################################################################################
# Student

class CreateStudentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Student created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def manage_student(request):
    # students = Student.objects.all()
    unique_grades = StudentClass.objects.values_list('grade', flat=True).distinct()

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            base_username = form.cleaned_data['name']
            # unique_username = generate_unique_username(base_username)
            user = CustomUser.objects.create(
                # username=unique_username,
                username=form.cleaned_data['phone'],
                is_student=True,
                is_staff=False,
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            student = form.save(commit=False)
            student.user = user
            student.added_by = request.user
            student.save()

            add_to_grade = StudentClass.objects.create(
                student=student,
                grade=student.grade
            )

            return redirect('manage_student')
    else:
        form = StudentForm()

    return render(request, 'manage_student.html', {'form': form, 'unique_grades': unique_grades})


@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def manage_student_byclass(request, grade):
    students = Student.objects.filter(grade=grade)
    return render(request, 'manage_student_byclass.html', {'students': students, 'grade': grade})

@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def all_student(request):
    students = Student.objects.all()
    return render(request, 'all_student.html', {'students': students})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('manage_student')

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
@require_POST
def update_student(request):
    """Update student data via AJAX."""
    student_id = request.POST.get('id')
    student = get_object_or_404(Student, id=student_id)

    # Update student details
    student.name = request.POST.get('name')
    student.phone = request.POST.get('phone')
    student.roll = request.POST.get('roll')
    student.grade = request.POST.get('grade')

    student_class = StudentClass.objects.filter(student=student).first()
    if student_class:
        student_class.grade = student.grade
        student_class.save()

    new_password = request.POST.get('password')
    if new_password:
        student.user.set_password(new_password)
        student.user.save()
    
    img = request.FILES.get('img')  # Handle file upload
    if img:
        student.img = img  # Update image if provided

    student.save()
    # Prepare data for the JSON response
    data = {
        'success': True,
        'id': student.id,
        'name': student.name,
        'phone': student.phone,
        'roll': student.roll,
        'grade': student.grade,
        'img': student.img.url if student.img else ''  # Handle image URL in response
    }

    return JsonResponse(data)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
def delete_class(request, grade):
    if request.method == "POST":
        # Delete all students from the given class (grade)
        StudentClass.objects.filter(grade=grade).delete()
        messages.success(request, f"All students from Class {grade} have been deleted.")
        return redirect('manage_student') 

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
@require_POST
def promote_class(request, grade):
    """Promote all students in the given class by incrementing their grade."""
    try:
        # Check if the grade is numeric and can be incremented
        new_grade = str(int(grade) + 1)  # Assuming numeric grades
        
        # Check if there are any students in the next grade
        if StudentClass.objects.filter(grade=new_grade).exists():
            messages.error(request, f"Cannot promote. There are already students in Class {new_grade}.")
            return redirect('manage_student')  # Redirect to the class list view
        
        # Promote students in StudentClass model
        students_in_class = StudentClass.objects.filter(grade=grade)
        for student_class in students_in_class:
            student_class.grade = new_grade
            student_class.save()

            # Also update the grade in the Student model
            student = student_class.student
            student.grade = new_grade
            student.save()

        messages.success(request, f"All students from Class {grade} have been promoted to Class {new_grade}.")
    except ValueError:
        messages.error(request, "Failed to promote students. Ensure the grade is numeric.")
    
    return redirect('your_class_list_view')  # Redirect to the class list view
# Student
############################################################################################################

############################################################################################################
# Salary

@login_required(login_url='teacher_login') 
@user_passes_test(lambda user: user.is_staff)
def generate_salary(request):
    current_date = timezone.now().date()  # Get the current date
    current_month = current_date.month
    current_year = current_date.year

    # Handle the POST request for salary generation
    if request.method == 'POST' and 'generate_salary' in request.POST:
        students = Student.objects.all()
        salary_records = []
        for student in students:
            if not MonthlySalary.objects.filter(student=student, date__year=current_year, date__month=current_month).exists():
                salary_records.append(
                    MonthlySalary(student=student, date=current_date, status='unpaid')
                )

        if salary_records:
            MonthlySalary.objects.bulk_create(salary_records)
            messages.success(request, 'Monthly salaries generated for all students who did not have one for this month.')
        else:
            messages.info(request, 'All students already have a salary record for this month.')

        return redirect('generate_salary')

    # Handle toggling of status
    if request.method == 'POST' and 'toggle_status' in request.POST:
        salary_id = request.POST.get('salary_id')
        salary = get_object_or_404(MonthlySalary, id=salary_id)
        if salary.status == 'paid':
            salary.status = 'unpaid'
        else:
            salary.status = 'paid'
        salary.save()
        return redirect('generate_salary')
    
    if request.method == 'POST' and 'delete_salary' in request.POST:
        salary_id = request.POST.get('delete_salary_id')
        salary = get_object_or_404(MonthlySalary, id=salary_id)
        salary.delete()
        messages.success(request, 'Salary record deleted successfully.')
        return redirect('generate_salary')


    # Get all salary records for the current month to display in the template
    monthly_salaries = MonthlySalary.objects.filter()

    return render(request, 'manage_salary.html', {
        'monthly_salaries': monthly_salaries,
        'current_month': current_month,
        'current_year': current_year,
    })


# Salary
############################################################################################################

from django.db.models import Q
from datetime import date

def exam_results_view(request):
    results = []
    total_marks_sum = 0
    exam_marks_sum = 0
    total_exam = 0

    if request.method == 'POST':
        grade = request.POST.get('grade')
        roll = request.POST.get('roll')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Query to filter results
        try:
            student = Student.objects.get(roll=roll, grade=grade)
            results = Result.objects.filter(
                Q(student=student) & 
                Q(exam__date__range=(start_date, end_date))
            )
            total_exam = results.count()
            total_marks_sum = sum(result.exam.total_marks for result in results)
            exam_marks_sum = sum(result.exam_marks for result in results)
        except Student.DoesNotExist:
            results = []

    return render(request, 'exam_results.html', {
        'results': results,
        'total_marks_sum': total_marks_sum,
        'exam_marks_sum': exam_marks_sum,
        'student_name': student.name if results else '',
        'student_roll': student.roll if results else '',
        'student_class': student.grade if results else '',
        'today': date.today(),
        'total_exam': total_exam,
    })

def manage_period(request):
    periods = Period.objects.all()

    if request.method == 'POST':
        if 'delete_period' in request.POST:
            period = get_object_or_404(Period, id=request.POST.get('delete_period'))
            period.delete()
            return redirect('manage_period')
        else:
            form = PeriodForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_period')
    else:
        form = PeriodForm()

    return render(request, 'manage_period.html', {'form': form, 'periods': periods})

def edit_period_ajax(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            period = get_object_or_404(Period, id=request.POST.get('period_id'))
            form = PeriodForm(request.POST, instance=period)

            if form.is_valid():
                form.save()
                data = {
                    'success': True,
                    'period_id': period.id,
                    'period_number': period.period_number,
                    # 'start_time': period.start_time.strftime('%I:%M %p'),
                    # 'end_time': period.end_time.strftime('%I:%M %p'),
                    'start_time': period.start_time,
                    'end_time': period.end_time,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

        else:
            return JsonResponse({'success': False, 'error': 'Not an AJAX request'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def manage_subject(request):
    subject = Subject.objects.all()

    if request.method == 'POST':
        if 'delete_subject' in request.POST:
            subject = get_object_or_404(Subject, id=request.POST.get('delete_subject'))
            subject.delete()
            return redirect('manage_subject')
        else:
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_subject')
    else:
        form = SubjectForm()

    return render(request, 'manage_subject.html', {'form': form, 'subjects': subject})

def edit_subject_ajax(request):
    if request.method == 'POST':

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            subject = get_object_or_404(Subject, id=request.POST.get('subject_id'))

            form = SubjectForm(request.POST, instance=subject)


            if form.is_valid():
                form.save()
                data = {
                    'success': True,
                    'subject_id': subject.id,
                    'subject_name': subject.subject,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

        else:
            return JsonResponse({'success': False, 'error': 'Not an AJAX request'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


