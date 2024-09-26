from rest_framework import serializers
from .models import AttendanceRecord, Exam, Lectures, MonthlySalary, Notes, Notice, Result, Routine, StudentClass, Teacher, Student, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username', 'date_joined', 'is_student', 'is_active']
    
class TeacherSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'name', 'phone', 'subject', 'img']

class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'name', 'phone', 'roll', 'grade', 'img']

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'content', 'date']

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['id', 'grade', 'subject', 'content', 'url', 'pdf', 'date']

class LecturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectures
        fields = ['id', 'grade', 'subject', 'content', 'url', 'date']

class RoutineSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()

    class Meta:
        model = Routine
        fields = ['period', 'start', 'end', 'day', 'subject', 'teacher', 'grade']

    def get_subject(self, obj):
        if obj.subject:
            return obj.subject.subject
        return None

    def get_teacher(self, obj):
        if obj.teacher:
            return obj.teacher.name
        return None
    
    def get_period(self, obj):
        if obj.period:
            return obj.period.period_number
        return None
    
    def get_start(self, obj):
        if obj.period:
            return obj.period.start_time
        return None
    
    def get_end(self, obj):
        if obj.period:
            return obj.period.end_time
        return None
    




class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    exam = ExamSerializer()
    student = StudentSerializer()
    highest_exam_marks = serializers.IntegerField()

    class Meta:
        model = Result
        fields = ['id', 'exam', 'student', 'exam_marks', 'position', 'symbol', 'highest_exam_marks']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'date', 'status']

class MonthlySalarySerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = MonthlySalary
        fields = ['id', 'student', 'date', 'status', 'amount', 'trxid']

class StudentCreateSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    img = serializers.ImageField(required=False)

    class Meta:
        model = Student
        fields = ['name', 'phone', 'grade', 'password', 'img']

    def validate_username(self, value):
        if not value.isnum():
            raise serializers.ValidationError("Username should contain only numbers.")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        # username = validated_data.pop('username')
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')

        # Create CustomUser instance
        user = CustomUser.objects.create_user(username=phone, password=password, is_student=True)

        # Create Student instance
        student = Student.objects.create(user=user, phone=phone, **validated_data)

        add_to_grade = StudentClass.objects.create(student=student, grade=student.grade)

        return student

