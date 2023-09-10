from django.db import models

# Table to store email templates
class EmailTemplate(models.Model):
    event_type = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()

# Table to store employee information
class Employee(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()  # Date of Birth
    join_date = models.DateField()  # Joining Date (for work anniversary)


# Table to log email sending status and errors
class EventLog(models.Model):
    event_type = models.CharField(max_length=50, null=True)
    recipient = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # Success, Error, Pending, etc.
    error_message = models.TextField(blank=True, null=True)

# Admin can read all tables via REST APIs
# You can use Django Rest Framework for this purpose.
