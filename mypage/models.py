from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username  # Display username in admin panel

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]  # Display the first 20 characters in admin panel

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')  # User who is reporting
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')  # Optional post being reported
    reported_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='reports_received')  # Optional user being reported
    message = models.TextField()  # Message detailing the reason for the report
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the report

    def __str__(self):
        return f'Report by {self.user.username} on {self.created_at}'
