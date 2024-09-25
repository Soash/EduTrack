from django import forms
from .models import CustomUser, Exam, Lectures, Notice, Period, Student, Subject, Teacher, Notes, Result
from django.forms import modelformset_factory
from django.contrib.auth.forms import PasswordChangeForm


class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.TextInput)
    is_superuser = forms.BooleanField(required=False)
    class Meta:
        model = Teacher
        fields = ['name', 'phone', 'subject', 'password', 'is_superuser', 'img']
        
class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.TextInput)

    class Meta:
        model = Student
        fields = ['name', 'phone', 'grade', 'password', 'img']
        labels = {
            'grade': 'Class',
        }


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'phone', 'img']
        labels = {
            'img': 'Image',
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None




class LectureForm(forms.ModelForm):
    class Meta:
        model = Lectures
        fields = ['grade', 'subject', 'content', 'url']
        widgets = {
            'content': forms.TextInput(),
        }
        labels = {
            'content': 'Title',
            'grade': 'Class',
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['grade', 'subject', 'content', 'url', 'pdf']
        widgets = {
            'content': forms.TextInput(),
            'pdf': forms.ClearableFileInput(attrs={'multiple': False}),
        }
        labels = {
            'content': 'Title',
            'grade': 'Class',
        }

# class RoutineForm(forms.ModelForm):
#     class Meta:
#         model = Routine
#         fields = ['grade', 'content', 'url', 'img']
#         widgets = {
#             'content': forms.TextInput(),
#         }
#         labels = {
#             'content': 'Title',
#             'grade': 'Class',
#             'img': 'Image',
#         }

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['content']
        widgets = {
            'content': forms.TextInput(),
        }

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['exam_marks', 'symbol']
ResultFormSet = modelformset_factory(Result, form=ResultForm, extra=0)

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'total_marks': forms.TextInput(),
        }
        labels = {
            'total_marks': 'Total Marks',
            'grade': 'Class',
            'name': 'Exam Name',
        }





class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['period_number', 'start_time', 'end_time']
        widgets = {
            'period_number': forms.TextInput(attrs={'type': 'text'}),
            'start_time': forms.TextInput(attrs={'type': 'time'}),
            'end_time': forms.TextInput(attrs={'type': 'time'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject']


