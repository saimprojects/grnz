from django.db import models

class Contact(models.Model):
    # Contact subject choices
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('product', 'Product Question'),
        ('order', 'Order Related'),
        ('return', 'Return/Exchange'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
        ('partnership', 'Partnership/Collaboration'),
        ('other', 'Other'),
    ]
    
    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Sender information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True, help_text='Optional')
    
    # Message content
    subject_type = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Attachment (optional)
    attachment = models.FileField(upload_to='contact_attachments/', null=True, blank=True)
    
    # Status tracking
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # Admin response
    admin_response = models.TextField(blank=True, null=True)
    admin_response_at = models.DateTimeField(blank=True, null=True)
    responded_by = models.CharField(max_length=100, blank=True, null=True, help_text='Admin name who responded')
    
    # Priority (for admin)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Internal notes
    internal_notes = models.TextField(blank=True, null=True, help_text='Private notes for admin only')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        return f"{self.name} - {self.subject[:50]} - {self.created_at.date()}"
    
    @property
    def subject_type_label(self):
        """Get human readable subject type"""
        return dict(self.SUBJECT_CHOICES).get(self.subject_type, self.subject_type)
    
    @property
    def priority_label(self):
        """Get human readable priority"""
        priority_colors = {
            'low': '🟢 Low',
            'medium': '🟡 Medium',
            'high': '🟠 High',
            'urgent': '🔴 Urgent',
        }
        return priority_colors.get(self.priority, self.priority)
    
    @property
    def response_status(self):
        """Get response status"""
        if self.admin_response:
            return 'Responded'
        elif self.is_resolved:
            return 'Resolved (No Response)'
        else:
            return 'Pending'
    
    def mark_as_resolved(self):
        """Mark contact as resolved"""
        self.is_resolved = True
        from django.utils import timezone
        self.resolved_at = timezone.now()
        self.save()
    
    def add_admin_response(self, response, admin_name=None):
        """Add admin response to contact"""
        from django.utils import timezone
        self.admin_response = response
        self.admin_response_at = timezone.now()
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if admin_name:
            self.responded_by = admin_name
        self.save()

class NewsletterSubscriber(models.Model):
    """Optional: Newsletter subscription"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
    
    def __str__(self):
        return self.email