# devblogg_core/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from devblogg_common.models import BaseModel, SoftDeleteModel

# --- ENUMS ---

class PostStatus(models.IntegerChoices):
    DRAFT = 0, _('Draft')
    PENDING = 1, _('Pending')
    IN_REVIEW = 2, _('In Review')
    PUBLISHED = 3, _('Published')
    REJECTED = 4, _('Rejected')

class ModerationAction(models.IntegerChoices):
    CLAIM_POST = 0, _('Claim Post')
    APPROVE_POST = 1, _('Approve Post')
    REJECT_POST = 2, _('Reject Post')
    BAN_USER = 3, _('Ban User')
    UNBAN_USER = 4, _('Unban User')

class ReportReason(models.IntegerChoices):
    SPAM = 0, _('Spam')
    INAPPROPRIATE_CONTENT = 1, _('Inappropriate Content')
    HARASSMENT = 2, _('Harassment')
    COPYRIGHT = 3, _('Copyright Violation')
    MISSINFORMATION = 4, _('Misinformation')
    OTHER = 5, _('Other')
# --- CONTENT MODULE ---

class Post(SoftDeleteModel):
    """
    Mapping Rule 2: Content Module
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=200)
    
    # Rule 2.B.1: Slug unique, collision handling logic in Service
    slug = models.SlugField(max_length=255, unique=True)
    
    summary = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField() # Markdown content
    
    status = models.IntegerField(
        choices=PostStatus.choices, 
        default=PostStatus.DRAFT,
        db_index=True
    )
    
    published_at = models.DateTimeField(null=True, blank=True)
    
    assigned_moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_posts'
    )
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['status', 'claimed_at']),
            models.Index(fields=['author', 'status']),
        ]

    def __str__(self):
        return self.title

# --- INTERACTION MODULE ---

class Comment(SoftDeleteModel):
    """
    Mapping Rule 3.B: Comments
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Hierarchy: Nested comments
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    content = models.TextField()

    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['post', 'created_at']), # Load comment list
        ]

class PostLike(BaseModel):
    """
    Mapping Rule 3.A: Likes
    One-Time Action per user per post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'post_likes'
        unique_together = ('post', 'user') # Constraint: User can like once

class PostBookmark(BaseModel):
    """
    Mapping Rule 3.A: Bookmarks
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'post_bookmarks'
        unique_together = ('post', 'user')

# --- MODERATION MODULE ---

class PostReport(BaseModel):
    """
    Mapping Rule 4.A: User Reporting
    Threshold logic check (>5) will be in Service.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason_code = models.IntegerField(choices=ReportReason.choices)
    reason = models.CharField(max_length=500)

    class Meta:
        db_table = 'post_reports'
        unique_together = ('post', 'user') # Constraint: User reports once per post

class ModerationLog(BaseModel):
    """
    Mapping Rule 5.C: Transparency & Logs
    Ghi lại mọi hành động: Approve, Reject, Ban, Claim.
    """
    action = models.IntegerField(choices=ModerationAction.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='moderation_actions'
    )
    
    # Target có thể là Post hoặc User
    target_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderation_records'
    )
    
    reason = models.TextField(null=True, blank=True) # Required for Reject
    
    # Metadata JSON to store additional info for clear understanding 
    meta_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'moderation_logs'
        indexes = [
            models.Index(fields=['target_post']),
            models.Index(fields=['actor']),
        ]