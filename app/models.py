from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator



class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    img = models.ImageField(upload_to='teacher_images/', blank=True, null=True)
    subject = models.CharField(max_length=50, null=True, blank=True)
    added_by = models.ForeignKey(CustomUser, related_name='teachers_added', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    roll = models.CharField(max_length=50, null=True, blank=True)
    grade = models.CharField(max_length=50)
    img = models.ImageField(upload_to='student_images/', blank=True, null=True)
    added_by = models.ForeignKey(CustomUser, related_name='students_added', on_delete=models.SET_NULL, null=True, blank=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.roll})"
    
    def save(self, *args, **kwargs):
        if not self.roll:
            last_student = Student.objects.filter(grade=self.grade).order_by('roll').last()

            if last_student:
                # Extract the last 3 digits of the roll number and increment by 1
                largest_number = int(last_student.roll[-3:]) + 1
            else:
                # If no students, start from 1
                largest_number = 1

            # Pad the number to 3 digits
            roll_number_padded = str(largest_number).zfill(3)

            self.roll = f"{roll_number_padded}"

        super(Student, self).save(*args, **kwargs)



class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        # ('vacation', 'Vacation'),
        # ('weekend', 'Weekend'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

#     def save(self, *args, **kwargs):
#         # Automatically mark weekends
#         if self.date.weekday() in (4, 5):  # Friday (4) and Saturday (5)
#             self.status = 'weekend'
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.student.name} - {self.date} - {self.get_status_display()}"

# class Vacation(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()

#     def __str__(self):
#         return f"Vacation for {self.student.name} from {self.start_date} to {self.end_date}"
    
class MonthlySalary(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trxid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Salary for {self.student.name} on {self.date} - {self.get_status_display()}"



class Notice(models.Model):
    content = models.TextField()
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.content

class Notes(models.Model):
    grade = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(auto_now=True)
    url = models.URLField(blank=True, null=True)
    added_by = models.ForeignKey(CustomUser, related_name='notes_added', on_delete=models.SET_NULL, null=True, blank=True)
    pdf = models.FileField(upload_to='notes_pdfs/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])], blank=True, null=True)

    def __str__(self):
        return f"{self.subject} - {self.grade}"

class Lectures(models.Model):
    grade = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    date = models.DateField(auto_now=True)
    added_by = models.ForeignKey(CustomUser, related_name='lectures_added', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.subject} - {self.grade}"
    
class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    grade = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.grade} - {self.subject} ({self.date})"

class Result(models.Model):
    SYMBOL_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    exam_marks = models.PositiveIntegerField(default=0)
    position = models.PositiveIntegerField(null=True, blank=True)
    symbol = models.CharField(max_length=10, choices=SYMBOL_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.exam.name} ({self.exam.date})"



class Period(models.Model):
    period_number = models.PositiveIntegerField()
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.period_number} Period - {self.start_time} to {self.end_time}'

class Subject(models.Model):
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.subject}'

class Routine(models.Model):
    DAY_CHOICES = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
    ]

    grade = models.CharField(max_length=50)
    day = models.CharField(max_length=9, choices=DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.grade} - {self.subject} - {self.teacher} - {self.day} - {self.period}"
    

class StudentClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.grade} - {self.student}"


    