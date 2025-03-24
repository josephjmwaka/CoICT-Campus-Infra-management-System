from django import forms
from .models import IssueReport

class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ["block_number", "floor_number", "room_number", "equipment_name", "problem_description", "equipment_count", "image"]
        widgets = {
            "equipment_name": forms.Select(attrs={"class": "form-select"}),
            "problem_description": forms.Select(attrs={"class": "form-select"}),
        }
