from django.db import models

class Trip(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Trip {self.id} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class DrowsinessEvent(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    duration = models.FloatField(help_text="How long eyes were closed in seconds")

    def __str__(self):
        return f"{self.severity} event at {self.timestamp.strftime('%H:%M:%S')}"