from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q
from .models import StudyGroup, GroupMembership, Video, UserProgress
from .forms import StudyGroupForm, VideoForm

def home(request):
    admin_groups = StudyGroup.objects.filter(is_admin_group=True).distinct()
    
    user_groups = []
    if request.user.is_authenticated:
        created = StudyGroup.objects.filter(creator=request.user)
        joined = StudyGroup.objects.filter(members__user=request.user, members__is_accepted=True)
        user_groups = (created | joined).distinct()
    
    # Generic motivational quotes as requested
    quotes = [
        "\"The beautiful thing about learning is that no one can take it away from you.\" - B.B. King",
        "\"Education is the most powerful weapon which you can use to change the world.\" - Nelson Mandela",
        "\"The expert in anything was once a beginner.\" - Helen Hayes",
        "\"It always seems impossible until it's done.\" - Nelson Mandela",
        "\"Don't let what you cannot do interfere with what you can do.\" - John Wooden"
    ]
    
    context = {
        'admin_groups': admin_groups,
        'user_groups': user_groups,
        'quotes': quotes,
    }
    return render(request, 'home.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'studyhub/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'studyhub/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            # In a real app, logic might differentiate admin and user during creation.
            # We'll allow is_admin_group=True if user is actual staff.
            if request.user.is_staff:
                group.is_admin_group = True
            group.save()
            # Add creator as a member automatically
            GroupMembership.objects.create(user=request.user, group=group, is_accepted=True)
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group_detail', group_id=group.group_id)
    else:
        form = StudyGroupForm()
    return render(request, 'studyhub/create_group.html', {'form': form})

def search_group(request):
    query = request.GET.get('q', '')
    if query:
        try:
            group = StudyGroup.objects.get(group_id=query)
            return redirect('group_detail', group_id=group.group_id)
        except StudyGroup.DoesNotExist:
            messages.error(request, "No group found with that ID.")
    return redirect('home')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, group_id=group_id)
    
    # Check membership
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
    except GroupMembership.DoesNotExist:
        membership = None

    # Handle join request
    if request.method == 'POST' and 'join_group' in request.POST:
        if not membership:
            is_accepted = group.is_admin_group # Auto-accept for admin groups
            GroupMembership.objects.create(user=request.user, group=group, is_accepted=is_accepted)
            if is_accepted:
                messages.success(request, f"You have joined {group.name}!")
            else:
                messages.success(request, f"Request to join {group.name} sent to the creator.")
            return redirect('group_detail', group_id=group.group_id)

    # Check access
    has_access = False
    if group.is_admin_group or group.creator == request.user:
        has_access = True
    elif membership and membership.is_accepted:
        has_access = True

    videos = group.videos.all()
    
    # Calculate Progress
    total_videos = videos.count()
    user_completed = 0
    group_progress_stats = None

    if has_access and total_videos > 0:
        completed_videos = UserProgress.objects.filter(user=request.user, video__in=videos, is_completed=True).values_list('video_id', flat=True)
        user_completed = completed_videos.count()
        
        # Add a flag to videos for the template to know if it's completed by current user
        for video in videos:
            video.is_completed_by_user = video.id in completed_videos

        # Calculate group overall stats: % of members who completed all videos
        total_members = group.members.filter(is_accepted=True).count()
        if total_members > 0:
            members_completed_all = 0
            # A bit heavy for scaling, but fine for now
            for member in group.members.filter(is_accepted=True):
                member_completed = UserProgress.objects.filter(user=member.user, video__in=videos, is_completed=True).count()
                if member_completed == total_videos:
                    members_completed_all += 1
            
            percent_completed_all = int((members_completed_all / total_members) * 100)
            group_progress_stats = f"{percent_completed_all}% members completed full module"

    context = {
        'group': group,
        'has_access': has_access,
        'membership': membership,
        'videos': videos,
        'total_videos': total_videos,
        'user_completed': user_completed,
        'progress_percent': int((user_completed / total_videos) * 100) if total_videos > 0 else 0,
        'group_progress_stats': group_progress_stats,
    }
    return render(request, 'studyhub/group_detail.html', context)

@login_required
def add_video(request, group_id):
    group = get_object_or_404(StudyGroup, group_id=group_id, creator=request.user)
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.group = group
            video.save()
            messages.success(request, f"Video '{video.title}' added to {group.name}.")
            return redirect('group_detail', group_id=group.group_id)
    else:
        form = VideoForm()
    return render(request, 'studyhub/add_video.html', {'form': form, 'group': group})

@login_required
def manage_requests(request, group_id):
    group = get_object_or_404(StudyGroup, group_id=group_id, creator=request.user)
    
    if request.method == 'POST':
        membership_id = request.POST.get('membership_id')
        action = request.POST.get('action')
        membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
        
        if action == 'accept':
            membership.is_accepted = True
            membership.save()
            messages.success(request, f"Accepted {membership.user.username} into {group.name}.")
        elif action == 'reject':
            membership.delete()
            messages.success(request, f"Rejected request from {membership.user.username}.")
            
        return redirect('manage_requests', group_id=group.group_id)
        
    pending_requests = group.members.filter(is_accepted=False)
    members = group.members.filter(is_accepted=True)
    
    context = {
        'group': group,
        'pending_requests': pending_requests,
        'members': members,
    }
    return render(request, 'studyhub/manage_requests.html', context)

@login_required
def mark_video(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        if video_id:
            video = get_object_or_404(Video, id=video_id)
            # Make sure user has access to this video's group
            has_access = video.group.is_admin_group or video.group.creator == request.user or \
                        GroupMembership.objects.filter(user=request.user, group=video.group, is_accepted=True).exists()
            
            if has_access:
                # Mark as completed
                UserProgress.objects.update_or_create(
                    user=request.user,
                    video=video,
                    defaults={'is_completed': True, 'completed_at': timezone.now()}
                )
                return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400)
