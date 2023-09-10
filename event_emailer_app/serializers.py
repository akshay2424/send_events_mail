from rest_framework import serializers
from .models import Employee, EmailTemplate, EventLog

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'

class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = '__all__'
