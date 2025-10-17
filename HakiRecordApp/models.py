from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Statement(models.Model):
    service_no = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100)
    dob = models.DateField()
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    INCIDENT_TYPES = [
        ('theft', 'Theft'),
        ('murder', 'Murder'),
        ('abuse', 'Child Abuse'),
        ('accident', 'Accident'),
    ]
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)

    incident_location = models.CharField(max_length=255)

    incident_date = models.DateField(default=timezone.now)

    INCIDENT_TIMES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]
    incident_time = models.CharField(max_length=20, choices=INCIDENT_TIMES)
    suspect_description = models.TextField(blank=True, null=True)
    incident_description = models.TextField(blank=True, null=True)
    incident_evidence = models.FileField(upload_to='evidence/')
    recorded_at = models.DateTimeField(auto_now_add=True)
    ob_number = models.CharField(max_length=30, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ob_number:
            today = timezone.localtime().date()
            # Count how many entries are recorded today
            count_today = Statement.objects.filter(
                recorded_at__date=today
            ).count() + 1
            # Generate OB number, e.g., "OB 1/14/10/2025"
            self.ob_number = f"OB {count_today}/{today.day}/{today.month}/{today.year}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Contact(models.Model):
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=100)
    contact_message = models.TextField()

    def __str__(self):
        return f"{self.contact_name} {self.contact_email}"

