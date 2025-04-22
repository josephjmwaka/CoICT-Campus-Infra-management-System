from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MaintenanceRequest, Equipment, Block, Floor, Room
from .forms import MaintenanceRequestForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
import os

@login_required
def home(request):
    blocks = Block.objects.all()
    if request.user.is_authenticated:
        user_requests = MaintenanceRequest.objects.filter(reported_by=request.user)
        completed_requests = user_requests.filter(status='COMPLETED')
        in_progress_requests = user_requests.filter(status='IN_PROGRESS')
        
        return render(request, 'infrastructure/home.html', {
            'blocks': blocks,
            'user_requests': user_requests,
            'completed_requests': completed_requests,
            'in_progress_requests': in_progress_requests,
        })
    return render(request, 'infrastructure/home.html', {'blocks': blocks})

@login_required
def my_issues(request):
    issues = MaintenanceRequest.objects.filter(reported_by=request.user).order_by('-created_at')
    return render(request, "infrastructure/my_issues.html", {"issues": issues})

@login_required
def report_issue(request):
    blocks = Block.objects.all()
    
    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.reported_by = request.user
            maintenance_request.save()
            
            # Send email notification
            send_mail(
                subject="Issue Report Submitted",
                message=f"Dear {request.user.username},\n\nYour issue report has been successfully submitted. Our team will review it soon.",
                from_email=os.getenv('MAIL_HOST_USER'),
                recipient_list=[os.getenv('MAIL_HOST_USER')], #valid email just for testing should be [request.user.email]
                fail_silently=False,
            )
            
            messages.success(request, "Your maintenance request has been submitted successfully!")
            return redirect('home')
    else:
        form = MaintenanceRequestForm(user=request.user)
    
    return render(request, "infrastructure/report_issue.html", {
        "form": form,
        "blocks": blocks
    })

def ajax_load_floors(request):
    block_id = request.GET.get('block')
    if not block_id:
        return JsonResponse({'html': '<option value="">Select a Floor</option>'})
    
    try:
        block = Block.objects.get(id=block_id)
        if not block.has_multiple_floors:
            return JsonResponse({'html': '<option value="">This block has no floors</option>'})
            
        floors = Floor.objects.filter(block_id=block_id).order_by('number')
        context = {'floors': floors}
        html = render_to_string('infrastructure/floor_dropdown_options.html', context)
        return JsonResponse({'html': html})
    except Exception as e:
        return JsonResponse({'html': f'<option value="">Error: {str(e)}</option>'})

def ajax_load_rooms(request):
    block_id = request.GET.get('block')
    floor_id = request.GET.get('floor')
    
    if not block_id:
        return JsonResponse({'html': '<option value="">Select a Room</option>'})
    
    try:
        rooms = Room.objects.filter(block_id=block_id)
        if floor_id:
            rooms = rooms.filter(floor_id=floor_id)
        else:
            # For blocks without floors
            rooms = rooms.filter(floor__isnull=True)
            
        rooms = rooms.order_by('number')
        context = {'rooms': rooms}
        html = render_to_string('infrastructure/room_dropdown_options.html', context)
        return JsonResponse({'html': html})
    except Exception as e:
        return JsonResponse({'html': f'<option value="">Error: {str(e)}</option>'})

def ajax_load_equipment(request):
    room_id = request.GET.get('room')
    if not room_id:
        return JsonResponse({'html': '<option value="">Select Equipment</option>'})
    
    try:
        equipment = Equipment.objects.filter(room_id=room_id).order_by('name')
        html = render_to_string('infrastructure/equipment_dropdown_options.html', {'equipment': equipment})
        return JsonResponse({'html': html})
    except Exception as e:
        return JsonResponse({'html': '<option value="">Error loading equipment</option>'})