from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Permission
from subscriptions.models import Subscription

from django.db.models import Count

class UserRole(models.Model):
    role = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True)
    
    def __str__(self):
        return self.role

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, null = True, blank = True)
    manager = models.ForeignKey("self", on_delete=models.CASCADE, null = True, blank=True)
    objects = CustomUserManager()
    template_limit = models.IntegerField(help_text="Limit of template creation", default = 1)
    campaign_limit = models.IntegerField(help_text="Limit of creating campaigns", default = 1)
    messages_limit = models.IntegerField(help_text="Limit of sending messages", default = 1)
    subscription = models.ForeignKey(Subscription, null = True, blank = True, on_delete = models.RESTRICT)

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
    
class OTP(models.Model):
    otp = models.CharField(max_length=20)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.otp
    
class ContactGroup(models.Model):
    group_name = models.CharField(max_length=200, help_text="Name of the group")

    def __str__(self):
        return self.group_name


class Contact(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the person")
    phone = models.CharField(max_length=16)
    contact_group = models.ForeignKey(ContactGroup, on_delete = models.CASCADE, help_text="Choose the group to add contact")

    def __str__(self):
        return self.name
    

class Template(models.Model):
    TEMPLATE_CATEGORIES = [
        ('UTILITY', 'UTILITY'),
        ('MARKETING', 'MARKETING'),
        ('AUTHENTICATION', 'AUTHENTICATION'),
    ]
    TEMPLATE_TYPE = [
        ('STANDARD', 'Standard'),
        ('MEDIA', 'Media'),
    ]

    name = models.CharField(max_length=255, help_text="WhatsApp template name")
    language = models.CharField(max_length=10, default="en_US", help_text="Language code, e.g., en_US")
    category = models.CharField(max_length=15, choices=TEMPLATE_CATEGORIES, 
    help_text="Template category")
    template_type = models.CharField(max_length=20, choices = TEMPLATE_TYPE, default = "Standard")
    body = models.TextField(help_text="Template body with placeholders like {{1}}, {{2}}")
    headerType = models.CharField(max_length = 20, default = "None")
    header = models.CharField(max_length=255, blank=True, null=True, help_text="Optional header text")
    header_media = models.FileField(upload_to = "media", blank = True, null = True)
    footer = models.CharField(max_length=255, blank=True, null=True, help_text="Optional footer text")

    button1 = models.JSONField(null=True, blank = True)
    button2 = models.JSONField(null=True, blank = True)
    button3 = models.JSONField(null=True, blank = True)
    button4 = models.JSONField(null=True, blank = True)
    approved = models.BooleanField(default=False, help_text="WhatsApp template approval status")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.language})"

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    name = models.CharField(max_length=255, help_text="Name of the campaign")
    budget = models.IntegerField(default = 100)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="campaigns")
    description = models.TextField(blank=True, null=True, help_text="Description of the campaign")
    to_group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Running")
    scheduled_time = models.DateTimeField(blank=True, null=True, help_text="Scheduled time to start the campaign")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class Message(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="messages", null = True, blank = True)
    recipient_phone = models.CharField(max_length=20, help_text="Recipient's WhatsApp phone number", blank = True)
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    response_id = models.CharField(max_length=255, blank=True, null=True, help_text="Message ID returned by WhatsApp API")
    response_text = models.TextField(blank=True, null=True, help_text="API response or error details")
    from_admin = models.BooleanField(default = True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.recipient_phone} - {self.status}"

class AccessToken(models.Model):
    token = models.TextField()

    def __str__(self):
        return self.token