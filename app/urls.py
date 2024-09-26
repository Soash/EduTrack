from django.urls import path
from .views import CreateStudentView, LecturesListView, NotesListView, NoticeListView, RoutinesForWeekView, StudentAttendanceView, StudentInfoView, StudentLogoutView, StudentResultView, StudentSalaryView, TeacherListView
from . import views

urlpatterns = [
    path('api/student-info/', StudentInfoView.as_view(), name='student-info'),
    path('api/student-result/', StudentResultView.as_view(), name='student-result'),
    path('api/student-attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    path('api/student-salary/', StudentSalaryView.as_view(), name='student-salary'),
    path('api/logout/', StudentLogoutView.as_view(), name='student_logout'),
    
    path('api/teacher-list/', TeacherListView.as_view(), name='teacher-list'),
    path('api/notices/', NoticeListView.as_view(), name='notice-list'),
    path('api/lectures/', LecturesListView.as_view(), name='lecture-list'),
    path('api/notes/', NotesListView.as_view(), name='notes-list'),
    path('api/routines/', RoutinesForWeekView.as_view(), name='routines-for-week'),

    path('api/create-student/', CreateStudentView.as_view(), name='create-student'),

    path('', views.home, name='home'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.logout_view, name='logout'),

    path('attendance/', views.attendance_record, name='attendance_record'),
    path('student/<str:status>/<int:id>/', views.mark_attendance, name='mark_absent'),

    path('manage-lecture/', views.manage_lecture, name='manage_lecture'),
    path('lecture/delete/<int:id>/', views.delete_lecture, name='delete_lecture'),
    path('lecture/update/', views.update_lecture, name='update_lecture'),

    path('manage-note/', views.manage_note, name='manage_note'),
    path('delete-note/<int:id>/', views.delete_note, name='delete_note'),
    path('note/update/', views.update_note, name='update_note'),

    path('manage-notice/', views.manage_notice, name='manage_notice'),
    path('delete-notice/<int:id>/', views.delete_notice, name='delete_notice'),
    path('notice/update/', views.update_notice, name='update_notice'),

    path('manage-exam/', views.manage_exam, name='manage_exam'),
    path('delete-exam/<int:id>/', views.delete_exam, name='delete_exam'),
    path('exam/update/', views.update_exam, name='update_exam'),
    path('exams/<int:exam_id>/update/', views.update_exam_results, name='update_exam_results'),
    path('exams/<int:exam_id>/view/', views.view_exam_results, name='view_exam_results'),
    path('exam-results/', views.exam_results_view, name='exam_results'),

    path('manage-teacher/', views.manage_teacher, name='manage_teacher'),
    path('delete-teacher/<int:id>/', views.delete_teacher, name='delete_teacher'),
    path('teacher/update/', views.update_teacher, name='update_teacher'),

    path('manage-student/', views.manage_student, name='manage_student'),
    path('manage-student-byclass/<int:grade>', views.manage_student_byclass, name='manage_student_byclass'),
    path('delete-student/<int:id>/', views.delete_student, name='delete_student'),
    path('student/update/', views.update_student, name='update_student'),
    path('delete-class/<str:grade>/', views.delete_class, name='delete_class'),
    path('all-student/', views.all_student, name='all_student'),
    path('promote-class/<str:grade>/', views.promote_class, name='promote_class'),

    path('generate-salary/', views.generate_salary, name='generate_salary'),
    path('toggle_salary_status/', views.toggle_salary_status, name='toggle_salary_status'),
    path('delete_salary/', views.delete_salary, name='delete_salary'),

    path('periods/', views.manage_period, name='manage_period'),
    path('period/edit/', views.edit_period_ajax, name='edit_period_ajax'),

    path('subject/', views.manage_subject, name='manage_subject'),
    path('subject/edit/', views.edit_subject_ajax, name='edit_subject_ajax'),

    path('routine/manage/', views.manage_routine, name='manage_routine'),
    path('routine/view/<str:grade>/', views.view_routine, name='view_routine'),
    path('routine/update/<int:id>/', views.update_routine, name='update_routine'),
    path('routine/delete/<int:grade>/', views.delete_routines, name='delete_routine'),
]


