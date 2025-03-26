from django.db import models
from django.contrib.auth.models import User

class IssueReport(models.Model):
    EQUIPMENT_CHOICES = [
        ("Projector", "Projector"),
        ("Fan", "Fan"),
        ("Sink", "Sink"),
        ("Light", "Light"),
        ("AC", "Air Conditioner"),
        ("Door", "Door"),
    ]

    PROBLEM_CHOICES = [
        ("Not Working", "Not Working"),
        ("Broken", "Broken"),
        ("Leaking", "Leaking"),
        ("Loose Connection", "Loose Connection"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Fixed', 'Fixed'),
    ]

    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    block_number = models.CharField(max_length=10)
    floor_number = models.CharField(max_length=10)
    room_number = models.CharField(max_length=10)
    equipment_name = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES, default="Other")
    problem_description = models.CharField(max_length=50, choices=PROBLEM_CHOICES, default="Other")
    equipment_count = models.PositiveIntegerField()
    image = models.ImageField(upload_to="issue_images/", blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment_name} in Room {self.room_number} - {self.problem_description}"

