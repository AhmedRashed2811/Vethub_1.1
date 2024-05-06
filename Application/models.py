
# ? -------------------------------------------------------------------------------------------------------IMPORTING LIBRARIES
from django.db import models
from django.core.files.storage import default_storage
from django.core.validators import RegexValidator,MaxValueValidator, MinValueValidator
from django.contrib.auth.models import  AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.utils import timezone
import os
from uuid import uuid4 
from django_resized import ResizedImageField
from PIL import Image


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        upload_to = self.path
        # Return the original filename without modifications
        return os.path.join(upload_to, filename)

def delete_file(path):
    if default_storage.exists(path):
        default_storage.delete(path)


#  -------------------------------------------------------------------------------------------------------MODELS

# -----------------------------------------------------------------------------USER
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    # Add custom fields
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=100, null=False, default="")
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^01[0-9]{9}$',
                message="Phone number must be entered in the format: '01*******'"
            )
        ],
        null =False, 
        unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


# -----------------------------------------------------------------------------CUSTOMER
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
    appointments_count = models.IntegerField(null=True,blank=True, default=0)
    
    def __str__(self):
        return self.user.email


# -----------------------------------------------------------------------------DOCTORS
class Doctor(models.Model):
    DAY_OFF = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday','Friday'),
        ('None', 'None')
    ]
    
    user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
    profile_photo = ResizedImageField(quality=80, upload_to=PathAndRename('Profile_Photos'), null=False, blank=False)
    certifications = ResizedImageField(size=[800, 600], quality=80, upload_to=PathAndRename('Certifications'), null=False, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    urgent_examination = models.BooleanField(default = False, null = False)
    city = models.CharField(max_length=150)
    location = models.CharField(max_length=1000, null=True,blank=True)
    governorate = models.CharField(max_length=50)
    offer_percentage = models.DecimalField(max_digits=2, decimal_places=2,default = 0.0, null=True,blank=True) 
    offer_end_date = models.DateField(null=True,blank=True)
    reviews = models.IntegerField(null=True,blank=True, default=0)
    day_off = models.CharField(max_length=10, choices=DAY_OFF)
    start_time = models.CharField(max_length=10, default='12:00 am')
    finish_time = models.CharField(max_length=10, default='11:30 pm')
    rating = models.DecimalField(
                            null=True,blank=True,
                            default=0,
                            max_digits=2,
                            decimal_places=1,
                            validators=[
                                MaxValueValidator(5),
                                MinValueValidator(0)
                        ])
    is_verified = models.BooleanField(default = False, null = False)
    appointments_count = models.IntegerField(null=True,blank=True, default=0)
    
    def __str__(self):
        return self.user.email
    
    def displayed_price(self):
        return self.price - (self.price * self.offer_percentage)
    
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
        
        # Get the profile photo path
        #profile_photo_path = str(self.profile_photo.path).replace('Images', 'Images\\Profile_Photos')
        profile_photo_path = self.profile_photo.path
        
        # Check if the profile photo file exists
        if os.path.exists(profile_photo_path):
            # Extract the directory part of the path
            
            # Open the profile photo image
            profile_photo_image = Image.open(profile_photo_path)

            # Rotate the image based on the EXIF orientation metadata
            exif = profile_photo_image._getexif()
            
            if exif:
                orientation = exif.get(0x0112)

            # Save the rotated image to the new path
            profile_photo_image.save(profile_photo_path)
        else:
            print("Profile photo file does not exist:", profile_photo_path)

        super().save(*args, **kwargs)


# -----------------------------------------------------------------------------APPOINTMENTS
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('On-Going', 'On-Going'),
        ('Done', 'Done'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_price = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.TextField( null=False, blank=False)
    time = models.TextField( null=False, blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    offline_customer_name = models.CharField(max_length=100, null=True, blank=True, default="")
    offline_customer_phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^01[0-9]{9}$',
                message="Phone number must be entered in the format: '01*******'"
            )
        ],
        null =True,
        blank =True, 
    )
    reported = models.BooleanField(default=False)
    
    def __str__(self):
        if self.offline_customer_name:
            return f"Appointment: {self.offline_customer_name} with {self.doctor.user.name} on {self.date} at {self.time}"
        
        return f"Appointment: {self.customer.user.name} with {self.doctor.user.name} on {self.date} at {self.time}"


# -----------------------------------------------------------------------------CHATS
class Chat(models.Model):
    SENDER_CHOICES = [
        ('Customer', 'Customer'),
        ('Doctor', 'Doctor'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    last_msg = models.TextField(default="",null=True, blank=True)
    last_msg_time = models.DateTimeField(default=timezone.now)
    last_msg_seen = models.BooleanField(default = False)
    last_msg_sender = models.CharField(max_length=10, choices=SENDER_CHOICES, default="Customer")
    
    def __str__(self):
        return f"{self.customer.user.name} with dr. {self.doctor.user.name}"


# -----------------------------------------------------------------------------MESSAGES
class ChatMessage(models.Model):
    
    content = models.TextField()
    msg_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_receiver")
    seen = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.content


# -----------------------------------------------------------------------------FEEDBACK
class Feedback(models.Model):
    QUESTION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Poor', 'Poor'),
    ]
    date = models.DateTimeField(auto_now_add=True)
    inappropriate = models.BooleanField(default = False)
    comment = models.TextField()
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    question1 = models.CharField(max_length=10, choices=QUESTION_CHOICES, default='Good')
    question2 = question2 = models.CharField(max_length=10, choices=QUESTION_CHOICES, default='Good')
    
    def __str__(self):
        return f"{self.customer.user.name} with dr. {self.doctor.user.name}"


# -----------------------------------------------------------------------------ADMIN
class Admin(models.Model):
    user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)

    def __str__(self):
        return self.user.email


# -----------------------------------------------------------------------------NEWS
class News(models.Model):
    information = models.TextField()
    image = models.ImageField( upload_to=PathAndRename('news'), null=False, blank=False)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return self.information


# -----------------------------------------------------------------------------SUPPORT TEAM MESSAGE
class SupportTeamMessage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default = False)

    def __str__(self):
        return f'Message from ({self.customer})'


# -----------------------------------------------------------------------------NOTIFICATION
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('CREATED', 'Appointment created'),
        ('CANCELED', 'Appointment canceled'),
        ('APPOINTMENT_DONE', 'Appointment done'),
        ('DOCTOR_CANCELED', 'Doctor canceled appointment'),
        ('REMINDER', 'Appointment reminder'),
        ('NEWS' , 'News added'),
        ('RESPONSE', 'Admin sent response' )
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.user.name} - {self.notification_type}'

    class Meta:
        ordering = ['-created_date', '-created_time']


# -----------------------------------------------------------------------------PET
class Pet(models.Model):
    PET_TYPE = [
        ('Cat', 'Cat'),
        ('Dog', 'Dog'),
        ('Turtle', 'Turtle'),
        ('Monkey', 'Monkey'),
        ('Other', 'Other')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True, default="")
    age = models.DecimalField(max_digits=5, decimal_places=2)
    type = models.CharField(max_length=10, choices=PET_TYPE, default='Other')
    
    def __str__(self):
        return self.name


# -----------------------------------------------------------------------------PET REPORTS
class PetPreviousReports(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    report = models.CharField(max_length=1000, null=True, blank=True, default="")
    dose1 = models.CharField(max_length=100, null=True, blank=True, default="")
    dose2 = models.CharField(max_length=100, null=True, blank=True, default="")
    dose3 = models.CharField(max_length=100, null=True, blank=True, default="")
    created_date = models.DateField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.pet.name



