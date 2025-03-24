from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import IssueReport
from .forms import IssueReportForm

def home(request):
    infrastructures = IssueReport.objects.all()
    return render(request, 'infrastructure/home.html', {'infrastructures': infrastructures})


@login_required
def report_issue(request):
    if request.method == "POST":
        form = IssueReportForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user  # Assign user to the report
            issue.save()
            return redirect("home")  # Redirect to home page after submission
    else:
        form = IssueReportForm()
    
    return render(request, "infrastructure/report_issue.html", {"form": form})

@login_required
def my_issues(request):
    issues = IssueReport.objects.filter(reported_by=request.user).order_by('-created_at')
    return render(request, "infrastructure/my_issues.html", {"issues": issues})


