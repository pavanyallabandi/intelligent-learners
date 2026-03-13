from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    # Custom user model in case we need to add fields later
    pass

class StudyGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    is_admin_group = models.BooleanField(default=False)
    group_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    is_accepted = models.BooleanField(default=False) # True immediately for admin groups, False otherwise until creator accepts
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending"
        return f"{self.user.username} in {self.group.name} - {status}"

class Video(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    youtube_id = models.CharField(max_length=100) # Extracted from the YouTube link
    order = models.IntegerField(default=0) # To maintain a roadmap sequence
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.group.name})"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        status = "Completed" if self.is_completed else "Not Completed"
        return f"{self.user.username} - {self.video.title}: {status}"
