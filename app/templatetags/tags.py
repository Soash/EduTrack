from datetime import datetime
from django import template
from app.models import AttendanceRecord, Routine

register = template.Library()

@register.filter
def get_attendance_status(student, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        attendance_record = AttendanceRecord.objects.get(student=student, date=date_obj)
        return attendance_record.status
    except AttendanceRecord.DoesNotExist:
        return 'absent'


# @register.simple_tag
# def get_routine_id(period_id, day, grade):
#     try:
#         routine = Routine.objects.get(period_id=period_id, day=day, grade=grade)
#         return routine.id
#     except Routine.DoesNotExist:
#         return None 

@register.simple_tag
def get_routine(period_id, day, grade):
    try:
        routine = Routine.objects.get(period_id=period_id, day=day, grade=grade)
        return routine
    except Routine.DoesNotExist:
        return None

