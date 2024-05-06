
# ? -------------------------------------------------------------------------------------------------------IMPORTING LIBRARIES
import json
import re
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.core.mail import EmailMessage
from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login as Login, logout as Logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .decorators import unauthenticated_user, allowed_users
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models.query_utils import Q
from django.db.models import Avg
from datetime import datetime, timedelta
from .tokens import *
from .models import *
from .forms import *
from .nlp import predict


# TODO -------------------------------------------------------------------------------------------------------CONTROLLERS

#  --------------------------------------------------------------------------------------------------VIEWS

# -----------------------------------------------------------------------------HOME PAGE
def index(request):
    doctors = Doctor.objects.filter(is_verified = True)
    doctors_count = doctors.count()
    news = News.objects.all()
    feedback_exist = False
    supportTeamMessageForm = SupportTeamMessageForm(request.POST or None)
    
    context = {
        "doctors": doctors,
        "feedback_exists": feedback_exist,
        "news": news,
        "doctors_count":doctors_count}
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            if supportTeamMessageForm.is_valid():
                SupportTeamMessage.objects.create(
                    message = supportTeamMessageForm.cleaned_data["message"],
                    customer = request.user.customer
                )
                messages.success(request, "Your Message is Sent Successfully, and Check your Notifications for any Updates...")
                return redirect('/')
        
        if request.user.groups.filter(name='Customers').exists():
            delayed_appointments = Appointment.objects.filter(customer = request.user.customer)
            appointments = delayed_appointments.filter(status = "Done")
            notifications = Notification.objects.filter(customer = request.user.customer)
            notifications_count = notifications.filter(is_read = False).count()
            feedbacks = []
            not_feedback_appointments = []
            supportTeamResponse = SupportTeamMessage.objects.filter(customer = request.user.customer)
            
            for appointment in delayed_appointments:
                
                notification_message1 = f'Reminder! You have an appointment with dr.({appointment.doctor.user.name}) after 3 days on ({appointment.date})'
                notification_message2 = f'Reminder! You have an appointment with dr.({appointment.doctor.user.name}) Tomorrow at ({appointment.time})'
                notification_exist1 = Notification.objects.filter(customer = request.user.customer, message=notification_message1)
                notification_exist2 = Notification.objects.filter(customer = request.user.customer, message=notification_message2)
                
                if notification_exist1:
                    pass
                elif notification_exist2:
                    pass
                else:
                    if days_until_appointment(appointment.date) == 3:
                        Notification.objects.create(customer=request.user.customer, notification_type='REMINDER', message=notification_message)
                        notifications_count += 1
                    
                    if days_until_appointment(appointment.date) == 1:
                        Notification.objects.create(customer=request.user.customer, notification_type='REMINDER', message=notification_message2)
                        notifications_count += 1
            
            for response in supportTeamResponse:
                if response.response:
                    notification_message3 = f'Message from admin: ({response.response})'
                    notification_exist3 = Notification.objects.filter(customer = request.user.customer, message=notification_message3)
                    
                    if notification_exist3:
                        pass
                    else:
                        Notification.objects.create(customer=request.user.customer, notification_type='RESPONSE', message=notification_message3)
                        notifications_count += 1
            
            temp = 0
            for appointment in appointments:
                feedback = Feedback.objects.filter(customer = request.user.customer, doctor = appointment.doctor)

                if not feedback:
                    feedbacks.append(feedback)
                    not_feedback_appointments.append(appointment)
                    temp+=1
            
            for appointment in not_feedback_appointments:
                if appointments and len(feedbacks) != 0:
                    feedback_exist = True
                    notification_message = f'Please Give Dr. {appointment.doctor.user.name} a Feedback'
                    notification_exist3 = Notification.objects.filter(customer = request.user.customer, message=notification_message)
                    if not notification_exist3:
                        Notification.objects.create(customer=request.user.customer, notification_type='APPOINTMENT_DONE', message=notification_message)
                        notifications_count += 1
            
            notifications_count = notifications_count + temp
            context = {
                "doctors": doctors,
                "not_feedback_appointments":not_feedback_appointments,
                "appointments": appointments,
                "feedback_exists": feedback_exist,
                "news": news,
                "doctors_count":doctors_count,
                "notifications": notifications,
                "notifications_count":notifications_count}
            
        elif request.user.groups.filter(name='Admins').exists():
            context = {
                "doctors": doctors,
                "news": news,
                "doctors_count":doctors_count}
    
    if request.method =="POST":
        governorate = request.POST.get("governorate")
        city = request.POST.get("city")
        urgent_examination = request.POST.get("urgent-examination")
        if urgent_examination == "Yes":
            urgent_examination = True
        elif urgent_examination == "No":
            urgent_examination = False
        if not governorate and not city and not urgent_examination:
            pass
        else:
            if governorate and city and urgent_examination:
                doctors = doctors.filter(governorate = governorate, city = city, urgent_examination = urgent_examination)
                doctors_count = doctors.count()
            if governorate and city and not urgent_examination:
                doctors = doctors.filter(governorate = governorate, city = city)
                doctors_count = doctors.count()
            if governorate and not city and not urgent_examination:
                doctors = doctors.filter(governorate = governorate)
                doctors_count = doctors.count()
            if governorate and not city and urgent_examination:
                doctors = doctors.filter(governorate = governorate, urgent_examination = urgent_examination)
                doctors_count = doctors.count()
            if not governorate and city and not urgent_examination:
                doctors = doctors.filter(city = city)
                doctors_count = doctors.count()
            if not governorate and city and urgent_examination:
                doctors = doctors.filter(city = city, urgent_examination = urgent_examination)
                doctors_count = doctors.count()
            if not governorate and not city and urgent_examination:
                doctors = doctors.filter(urgent_examination = urgent_examination)
                doctors_count = doctors.count()
                
            context["doctors"] = doctors
            context["doctors_count"] = doctors_count

    return render(request, 'index.html', context)


# -----------------------------------------------------------------------------DOCTOR DETAILS & CREATE APPOINTMENT
def doctor_details(request, doctor_id):
    doctor1 = get_object_or_404(User, pk=doctor_id)
    feedbacks = Feedback.objects.filter(doctor = doctor1.doctor)
    appointments = Appointment.objects.filter(doctor = doctor1.doctor)
    rating = ""
    doctor_rating = int(round(doctor1.doctor.rating))
    remaining = 5-doctor_rating
    times = []
    time = {}
    start_time_str = doctor1.doctor.start_time
    finish_time_str = doctor1.doctor.finish_time

    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
    finish_time = datetime.strptime(finish_time_str, '%I:%M %p').time()
    
    reservation_times = ""

    temp_counter = 0
    current_time = start_time
    while current_time != finish_time:
        reservation_times += (f'<p class="time"><span>{str(current_time.strftime('%I:%M %p').replace("PM", "pm").replace("AM", "am"))}</span></p>')
        current_time = (datetime.combine(datetime.min, current_time) + timedelta(minutes=30)).time()
        temp_counter += 1
    reservation_times += (f'<p class="time"><span>{finish_time_str}</span></p>')
    temp_counter += 1
    
    for appointment in appointments:
        time["time"] = appointment.time
        time["date"] = appointment.date
        
        times.append(time)
        time = {}
        
    for i in range(0, doctor_rating):
        rating+='<i class="fa-solid fa-star checked"></i>'
    
    for i in range(0, remaining):
        rating+='<i class="fa-regular fa-star checked"></i>'
        
    doctor_rating = rating
    rating = ""
    feedback_list= []
    new_feedback = {}
    remaining = 0
    
    for feedback in reversed(feedbacks):
        rating = ""
        new_feedback["name"] = feedback.customer.user.name
        new_feedback["date"] = feedback.date
        new_feedback["comment"] = feedback.comment
        rate = int(feedback.rating)
        remaining = 5- rate
        for i in range(0, rate):
            rating+='<i class="fa-solid fa-star checked"></i>'
        
        for i in range(0, remaining):
            rating+='<i class="fa-regular fa-star checked"></i>'
        
        new_feedback["rating"] = rating
        feedback_list.append(new_feedback)
        new_feedback = {}
    
    
    location_url = doctor1.doctor.location
    pattern = r"mlat=([-+]?\d*\.\d+|\d+)&mlon=([-+]?\d*\.\d+|\d+)"
    match = re.search(pattern, location_url)

    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
    
    bbox_latitude_min = latitude - 0.015
    bbox_latitude_max = latitude + 0.015
    bbox_longitude_min = longitude - 0.015
    bbox_longitude_max = longitude + 0.015
    
    if request.method == 'POST':
        customer_id = request.POST.get('user_id')
        doctor_id = request.POST.get('doctor_id')
        doctor_price = float(request.POST.get('doctor_price'))
        offer_percentage = float(request.POST.get('offer_percentage'))
        doctor_offer_price = doctor_price - (doctor_price*offer_percentage)
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        if customer_id is None or not customer_id.isdigit():
            return redirect('/login')
        
        customer = User.objects.filter(id=customer_id).first()
        customer = Customer.objects.filter(user = customer).first()
        doctor = Doctor.objects.filter(user = doctor1).first()

        Appointment.objects.create(
            customer=customer,
            doctor=doctor,
            appointment_price=doctor_offer_price,
            date=date,
            time=time
        )
        
        customer.appointments_count += 1
        customer.save()
        
        notification_message = f'Your appointment with Dr. {doctor.user.name} has been successfully scheduled for {date} at {time}.'
        Notification.objects.create(customer=customer, notification_type='CREATED', message=notification_message)
        return redirect('/')
    
    else:    
        return render(request, 'doctor_details.html', {'doctor': doctor1, 'feedbacks_count': feedbacks.count(), 'latitude': latitude, 'longitude': longitude, 'latitude': latitude,
        'longitude': longitude,
        'bbox_latitude_min': bbox_latitude_min,
        'bbox_latitude_max': bbox_latitude_max,
        'bbox_longitude_min': bbox_longitude_min,
        'bbox_longitude_max': bbox_longitude_max,
        "feedback_list": feedback_list,
        "doctor_rating":doctor_rating,
        "appointments":times,
        "reservation_times":reservation_times,
        "days_counter": temp_counter}
        )


# -----------------------------------------------------------------------------SIGN-UP
@unauthenticated_user
def signup(request):
    return render(request, "SignUp.html")


# -----------------------------------------------------------------------------CUSTOMER SIGN-UP
@unauthenticated_user
def customer_register(request):
    if request.method == 'POST':
        email = request.POST.get("Email")
        name = request.POST.get("Name")
        phone_number = request.POST.get("PhoneNumber")
        password1 = request.POST.get("Password1")
    
        if  (User.objects.filter(email=email) or User.objects.filter(phone_number=phone_number)):
            messages.info(request, "User Already Exists")
            return redirect('login')

        hashed_password = make_password(password1)
        
        user = User.objects.create(
                        email=email,
                        name=name,
                        phone_number=phone_number,
                        password = hashed_password 
                    )
        
        customer = Customer.objects.create(
            user = user,
        )
        
        custom_user_instances = []
        user.is_active = False
        user.save()
        activate_email(request, user,user.email )
        custom_user_instances.append(user)
        group = Group.objects.get(name='Customers')
        group.user_set.add(user)
        first_custom_user_instance = custom_user_instances[0] if custom_user_instances else None
        
        customer.user = first_custom_user_instance
        customer.is_verified = False
        customer.save()
        
        messages.success(request, "Account is Created Successfully")
        return redirect('/login')

    return render(request, 'customer_register.html')


# -----------------------------------------------------------------------------DOCTOR SIGN-UP
@unauthenticated_user
def doctor_register(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        password1 = request.POST.get("password1")
        governorate = request.POST.get("governorate")
        city = request.POST.get("city")
        profile_photo = request.FILES.get("profile_photo")
        certifications = request.FILES.get("certification")
        price = request.POST.get("price")
        urgent_examination = request.POST.get("urgent-examination")
        description = request.POST.get("Description")
        location = request.POST.get('location')
        day_off = request.POST.get('day-off')
        start_time = request.POST.get('start-time')
        finish_time = request.POST.get('finish-time')
        
        if  (User.objects.filter(email=email) or User.objects.filter(phone_number=phone_number)):
            messages.info(request, "User Already Exists")
            return redirect('login')
    
        hashed_password = make_password(password1)
        
        user = User.objects.create(
                        email=email,
                        name=name,
                        phone_number=phone_number,
                        password = hashed_password 
                    )
        
        doctor = Doctor.objects.create(
            user = user,
            governorate = governorate,
            city = city,
            profile_photo = profile_photo,
            certifications = certifications,
            price = price,
            urgent_examination = urgent_examination,
            description = description,
            location = location,
            day_off = day_off,
            start_time = start_time,
            finish_time = finish_time
        )
        
        custom_user_instances = []
        user.is_active = False
        activate_email(request, user,user.email )
        user.save()
        custom_user_instances.append(user)
        group = Group.objects.get(name='Doctors')
        group.user_set.add(user)
        first_custom_user_instance = custom_user_instances[0] if custom_user_instances else None
        doctor.user = first_custom_user_instance
        doctor.save()
        messages.warning(request, "Your Certification is Being Verified Also")
        return redirect('/login')
        
    return render(request, 'doctor_register.html')


# -----------------------------------------------------------------------------LOGIN
@unauthenticated_user
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            try:
                if hasattr(user, 'doctor'):
                    if user.doctor.is_verified:
                        Login(request, user)
                        messages.success(request, "You are Logged In Successfully!")
                        return redirect(get_redirect_url(request))
                    else:
                        messages.warning(request, "Not Verified Yet")
                elif hasattr(user, 'customer'):
                    if user.is_active:
                        Login(request, user)
                        messages.success(request, "You are Logged In Successfully!")
                        return redirect(get_redirect_url(request))
                    else:
                        messages.error(request, "Verify your Email First")
                        return render(request, 'login.html')
                    
                elif hasattr(user, "admin"):
                    Login(request, user)
                    return redirect(get_redirect_url(request))
                
            except ObjectDoesNotExist:
                messages.info(request, "User has no doctor.")
        else:
            messages.error(request, "Not Correct Please Try Again")
            
    if 'HTTP_REFERER' in request.META:
        request.session['referrer'] = request.META.get('HTTP_REFERER')
            
    return render(request, 'login.html')


# -----------------------------------------------------------------------------EDIT DOCTOR
@allowed_users(allowed_roles=["Doctors", "Admins"])
@login_required(login_url='login')
def edit_doctor(request, doctor_id):
    doctor_user = get_object_or_404(User, pk=doctor_id)
    doctor = doctor_user.doctor  
    
    latitude = ""
    longitude = ""
    location_url = doctor.location
    pattern = r"mlat=([-+]?\d*\.\d+|\d+)&mlon=([-+]?\d*\.\d+|\d+)"
    match = re.search(pattern, location_url)
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
    bbox_latitude_min = latitude - 0.015
    bbox_latitude_max = latitude + 0.015
    bbox_longitude_min = longitude - 0.015
    bbox_longitude_max = longitude + 0.015
    
    if request.method == 'POST':
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        governorate = request.POST.get("governorate")
        city = request.POST.get("city")
        price = request.POST.get("price")
        urgent_examination = request.POST.get("urgent-examination")
        description = request.POST.get("Description")
        image_exist = False
        try:
            profile_photo = request.FILES['profile_photo']
            image_exist = True
        except:
            pass
        location = request.POST.get('location')
        
        if not city and not governorate :
            city = doctor.city
            governorate = doctor.governorate
            
        if city and not governorate:
            governorate = doctor.governorate
            
        if not city and governorate:
            city = doctor.city
        
        if phone_number != doctor_user.phone_number:
            temp = User.objects.filter(phone_number = phone_number).count()
            if temp != 0:
                messages.error(request, "This Number is already Exists")
                temp = 0
                if request.user.groups.filter(name='Admins').exists():
                    return redirect('/admin_panel')
                
                return redirect("edit_doctor", doctor_id=request.user.id)
        
        doctor_user.name = name
        doctor_user.phone_number = phone_number
        doctor.governorate = governorate
        doctor.city = city
        doctor.price = price
        doctor.urgent_examination = urgent_examination
        doctor.description = description
        
        try:
            if (image_exist):
                os.remove(doctor.profile_photo.path)
            doctor.profile_photo = profile_photo
        except:
            pass
        
        doctor.location = location
        
        doctor_user.save()
        doctor.save()
        messages.success(request, "Account is Updated Successfully")
        
        if request.user.groups.filter(name='Admins').exists():
            return redirect('/admin_panel')
        
        return redirect('/')
        
    return render(request, 'edit_doctor.html', {"user":doctor_user, "doctor":doctor,'latitude': latitude, 'longitude': longitude, 'latitude': latitude,
        'longitude': longitude,
        'bbox_latitude_min': bbox_latitude_min,
        'bbox_latitude_max': bbox_latitude_max,
        'bbox_longitude_min': bbox_longitude_min,
        'bbox_longitude_max': bbox_longitude_max,})


# -----------------------------------------------------------------------------EDIT CUSTOMER
@allowed_users(allowed_roles=["Customers", "Admins"])
@login_required(login_url='login')
def edit_customer(request, customer_id):
    
    customer_user = get_object_or_404(User, pk=customer_id)
    customer = customer_user.customer  
    appointments_count = customer.appointments_count
        
    if request.method == 'POST':
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        
        if(phone_number == customer_user.phone_number):
            customer_user.name = name
            customer_user.save()
            if request.user.groups.filter(name='Admins').exists():
                return redirect('/admin_panel')
            
            messages.success(request, "Account is Updated Successfully")
            return redirect("/") 
            
        temp = User.objects.filter(phone_number = phone_number).count()
        if temp != 0:
            messages.error(request, "This Number is already Exists")
            temp = 0
            return redirect("edit_customer", customer_id=request.user.id)
        
        else:
            customer_user.name = name
            customer_user.phone_number = phone_number
            customer_user.save()
            
            if request.user.groups.filter(name='Admins').exists():
                return redirect('/admin_panel')
            
            messages.success(request, "Account is Updated Successfully")
            
            return redirect("/")
        
    
    return render(request, 'edit_customer.html', { "appointments_count":appointments_count,"customer":customer_user})


# -----------------------------------------------------------------------------CLINIC MANAGEMENT SYSTEM
@login_required(login_url='login')
@allowed_users(allowed_roles=["Doctors"])
def clinic_management_system(request):
    doctor_user = User.objects.filter(id=request.user.id).first()
    doctor = Doctor.objects.filter(user = doctor_user).first()
    doctor_appointments = Appointment.objects.filter(doctor=doctor)
    appointments_done_count = doctor_appointments.filter(status = "Pending").count()
    if appointments_done_count == 0:
        appointments_done_count = ""
    feedbacks = Feedback.objects.filter(doctor = doctor)
    rating = ""
    feedback_list= []
    new_feedback = {}
    remaining = 0
    if doctor.offer_percentage == 0:
        offer_exist = False
    elif doctor.offer_percentage != 0:
        offer_exist = True
    
    for feedback in reversed(feedbacks):
        rating = ""
        new_feedback["name"] = feedback.customer.user.name
        new_feedback["date"] = feedback.date
        new_feedback["comment"] = feedback.comment
        rate = int(feedback.rating)
        remaining = 5- rate
        for i in range(0, rate):
            rating+='<i class="fa-solid fa-star checked"></i>'
        
        for i in range(0, remaining):
            rating+='<i class="fa-regular fa-star checked"></i>'
        
        new_feedback["rating"] = rating
        feedback_list.append(new_feedback)
        new_feedback = {}
        
    
    start_time_str = doctor.start_time
    finish_time_str = doctor.finish_time
    
    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
    finish_time = datetime.strptime(finish_time_str, '%I:%M %p').time()
    
    reservation_times = ""
    temp_counter = 0
    current_time = start_time
    while current_time != finish_time:
        reservation_times += (f'<p class="time"><span>{str(current_time.strftime('%I:%M %p').replace("PM", "pm").replace("AM", "am"))}</span></p>')
        current_time = (datetime.combine(datetime.min, current_time) + timedelta(minutes=30)).time()
        temp_counter += 1
    # Add the finish time to the list
    reservation_times += (f'<p class="time"><span>{finish_time_str}</span></p>')
    temp_counter += 1

    times = []
    time = {}
    
    for appointment in doctor_appointments:
        time["time"] = appointment.time
        time["date"] = appointment.date
        
        times.append(time)
        time = {}
    
    if request.method == "POST":
        day_off = request.POST.get("day-off")
        changed_start_time = request.POST.get("start-time")
        changed_finish_time = request.POST.get("finish-time")
        doctor.day_off = day_off
        doctor.start_time = changed_start_time
        doctor.finish_time = changed_finish_time
        doctor.save()
        
        messages.success(request, "Clinic Information is Updated Successfully")
        
        return redirect("clinic_management_system")

    context = {
        "doctor_appointments":doctor_appointments,
        "offer_exist":offer_exist,
        "feedback_list": feedback_list,
        "reservation_times":reservation_times,
        "days_counter": temp_counter,
        "appointments":times,
        "offer_percentage": int(doctor.offer_percentage *100),
        "appointments_done_count":appointments_done_count}
    
    return render(request, 'clinic_management_system.html', context)


# -----------------------------------------------------------------------------CHATS 
@allowed_users(allowed_roles=["Doctors","Customers"])
@login_required(login_url='login')
def chats(request):
    
    user = request.user
    if user.groups.filter(name='Customers').exists():
        customer = request.user.customer
        chats = Chat.objects.filter(customer = customer)
        returned_chats = []
        for chat in chats:
            if chat.last_msg == "":
                chat.delete()
                continue
            
            returned_chats.append(chat)
        context = {"user": customer, "chats": returned_chats}
        return render(request, 'chats.html', context)
    
    if user.groups.filter(name='Doctors').exists():
        doctor = request.user.doctor
        chats = Chat.objects.filter(doctor = doctor)
        returned_chats = []
        for chat in chats:
            if chat.last_msg == "":
                chat.delete()
                continue
            
            returned_chats.append(chat)
        context = {"user": doctor, "chats": returned_chats}
        return render(request, 'chats.html', context)
        
    return render(request, 'chats.html')


# -----------------------------------------------------------------------------CHAT
@allowed_users(allowed_roles=["Doctors","Customers"])
@login_required(login_url='login')
def chat_details(request, receiver_id):
    user = request.user
    
    if user.groups.filter(name='Customers').exists():
        customer = request.user.customer
        doctor = get_object_or_404(User, pk=receiver_id)
        chat = Chat.objects.filter(customer = customer, doctor = doctor.doctor).first()
        
        if chat.last_msg_sender == "Doctor":
            chat.last_msg_seen = True
            
        chat.save() 
        received_messages = ChatMessage.objects.filter(msg_sender = doctor, msg_receiver = user)
        messages = ChatMessage.objects.filter(chat=chat)

        context = {
            "chat":chat,
            "sender": customer,
            "receiver": doctor, 
            "customer":customer,
            "doctor": doctor,
            "messages":messages,
            "number_of_received_messages": received_messages.count()}
        return render(request, 'chat_details.html', context)
    
    if user.groups.filter(name='Doctors').exists():
        doctor = request.user.doctor
        customer = get_object_or_404(User, pk=receiver_id)
        chat = Chat.objects.filter(customer = customer.customer, doctor = doctor).first()
        
        if chat.last_msg_sender == "Customer":
            chat.last_msg_seen = True
            
        chat.save() 
        
        
        context = {"sender": doctor, "receiver": customer}
        received_messages = ChatMessage.objects.filter(msg_sender = customer, msg_receiver = user)
        messages = ChatMessage.objects.filter(chat=chat)

        context = {
            "chat":chat,
            "sender": doctor,
            "receiver": customer,
            "customer":customer,
            "doctor": doctor,
            "messages":messages,
            "number_of_received_messages": received_messages.count()}
        return render(request, 'chat_details.html', context)
    
    return render(request, 'index.html')


# -----------------------------------------------------------------------------FEEDBACK
@allowed_users(allowed_roles=["Customers"])
@login_required(login_url='login')
def feedback(request, doctor_id):
    customer = request.user.customer
    doctor = User.objects.filter(id=doctor_id).first().doctor
    bad_word_exist = False
    if request.method == 'POST':
        question1 = request.POST.get("question1")
        question2 = request.POST.get("question2")
        comment = request.POST.get("comment")
        rating = request.POST.get("doctor-rating")
        
        bad_words = ["fuck",  "الخرا", "وسخ", "خول", "عرص", "يتمنيك" , "خرا", "متناكة", "نتن"]
        for word in bad_words:
            if word in comment.split():
                bad_word_exist = True
        if bad_word_exist:
            Feedback.objects.create(
                customer = customer,
                doctor = doctor,
                rating = rating,
                comment = comment,
                question1 = question1,
                question2 = question2,
                inappropriate = True
            )
        else:
            Feedback.objects.create(
                customer = customer,
                doctor = doctor,
                rating = rating,
                comment = comment,
                question1 = question1,
                question2 = question2
            )
            
        existing_ratings = Feedback.objects.filter(doctor=doctor)
        new_rating = existing_ratings.aggregate(Avg('rating'))['rating__avg']
        if new_rating is not None:
            doctor.rating = round(new_rating, 1)
        else:
            doctor.rating = 0 
        doctor.save()
        messages.info(request, "Thanks for your Feedback...")
        return redirect('/')
    return render(request, 'Feedback.html')


# -----------------------------------------------------------------------------CUSTOMER PREVIOUS APPOINTMENTS
@allowed_users(allowed_roles=["Customers"])
@login_required(login_url='login')
def customer_previous_appointments(request):
    customer = request.user.customer
    appointments = Appointment.objects.filter(customer = customer)
    context = {"appointments": appointments}
    feedback_exist = False
    feedbacks = []
    not_feedback_appointments = []
    
    for appointment in appointments:
        
        feedback = Feedback.objects.filter(customer = customer, doctor = appointment.doctor)
        if not feedback:
            feedbacks.append(feedback)
            not_feedback_appointments.append(appointment)
            
    if appointments and len(feedbacks) != 0:
        feedback_exist = True
        
    context = {"not_feedback_appointments":not_feedback_appointments, "appointments": appointments, "feedback_exists": feedback_exist}
    
    return render(request, "customer_previous_appointments.html", context)


# -----------------------------------------------------------------------------ADMIN PANEL
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def admin_panel(request):
    customers = Customer.objects.all()
    appointments = Appointment.objects.all()
    all_doctors = Doctor.objects.all()
    doctors = all_doctors.filter(is_verified = True)
    inappropriate_reviews = Feedback.objects.filter(inappropriate = True)
    feedback_list = []
    inappropriate_feedback = {}
    inappropriate_feedbacks = []
    news = News.objects.all()
    new_doctors = all_doctors.filter(is_verified = False)
    supportTeamMessages = SupportTeamMessage.objects.filter(answered = False)
    supportTeamMessages_count = supportTeamMessages.count()
    inappropriate_reviews_count = inappropriate_reviews.count()
    customers_count = customers.count()
    appointments_count = appointments.count()
    doctors_count = doctors.count()
    new_doctors_count = new_doctors.count()
    
    if new_doctors_count == 0: new_doctors_count = ""
    if inappropriate_reviews_count == 0: inappropriate_reviews_count = ""
    if supportTeamMessages_count == 0: supportTeamMessages_count = ""

    
    for feedback in (inappropriate_reviews):
        rating = ""
        rate = int(feedback.rating)
        remaining = 5- rate
        for i in range(0, rate):
            rating+='<i class="fa-solid fa-star checked"></i>'
        
        for i in range(0, remaining):
            rating+='<i class="fa-regular fa-star checked"></i>'
        
        feedback_list.append(rating)
    
    counter = 0
    for feedback in inappropriate_reviews:
        inappropriate_feedback["id"] = feedback.id
        inappropriate_feedback["review"] = feedback
        inappropriate_feedback["customer"] = feedback.customer
        inappropriate_feedback["date"] = feedback.date
        inappropriate_feedback["doctor"] = feedback.doctor
        inappropriate_feedback["comment"] = feedback.comment
        inappropriate_feedback["rating"] = feedback_list[counter]
        inappropriate_feedbacks.append(inappropriate_feedback)
        inappropriate_feedback = {}
        counter += 1
    

    
    
    context = {
        'customers': customers,
        'doctors': doctors,
        'appointments': appointments,
        'inappropriate_reviews':inappropriate_reviews,
        'supportTeamMessages': supportTeamMessages,
        'inappropriate_feedbacks':inappropriate_feedbacks,
        'news':news,
        "new_doctors":new_doctors,
        "customers_count":customers_count,
        "doctors_count":doctors_count,
        "inappropriate_reviews_count":inappropriate_reviews_count,
        "appointments_count":appointments_count,
        "new_doctors_count":new_doctors_count,
        "supportTeamMessages_count":supportTeamMessages_count
        }
    
    return render(request, 'admin_panel.html', context)


# -----------------------------------------------------------------------------ADMIN REGISTER
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def admin_register(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        name = request.POST.get("name")
        phone_number = request.POST.get("phoneNumber")
        password = request.POST.get("password")
        
        if  (User.objects.filter(email=email) or User.objects.filter(phone_number=phone_number)):
            messages.info(request, "User Already Exists")
            return redirect('admin_panel')
        
        password = make_password(password)
        
        user = User.objects.create(
                        email=email,
                        name=name,
                        phone_number=phone_number,
                        password = password 
                    )
        
        admin = Admin.objects.create(
            user = user,
        )
        
        custom_user_instances = []
        user.save()
        custom_user_instances.append(user)
        group = Group.objects.get(name='Admins')
        group.user_set.add(user)
        first_custom_user_instance = custom_user_instances[0] if custom_user_instances else None
        
        admin.user = first_custom_user_instance
        admin.save()
        
        messages.success(request, f"New Admin ({name}) is Created Successfully")
        return redirect('/')


# -----------------------------------------------------------------------------MANAGE NEWS
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def manage_news(request):
    if request.method == 'POST':
        image = request.FILES.get("news-image")
        description = request.POST.get("news-description")
        News.objects.create(image = image, information = description)

        notification_message = f'New news: {description}. Check it out now!'
        customers = Customer.objects.all()
        for customer in customers:
            Notification.objects.create(customer=customer, notification_type='NEWS', message=notification_message)
        
        messages.success(request, "News is Added Successfully...")
        return redirect('/')
        
    
    return redirect('/admin_panel')


# -----------------------------------------------------------------------------CHATBOT
@allowed_users(allowed_roles=["Customers"])
@login_required(login_url='login')
def chatbot(request):
    if request.method == 'POST':
        user_input = json.loads(request.body)
        new_message = user_input["message"]
        chat_response = predict(new_message)
        return JsonResponse({'response': chat_response})


# -----------------------------------------------------------------------------CREATE PET
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def create_pet(request, customer_id):
    customer_user = get_object_or_404(User, pk=customer_id)
    customer = customer_user.customer
    if request.method == 'POST':
        # Access POST data
        name = request.POST.get("name")
        age = request.POST.get("age")
        pet_type = request.POST.get("type")
        
        # Create a new Pet instance
        pet = Pet.objects.create(
            customer=customer,
            name=name,
            age=age,
            type=pet_type,
        )
        # Optionally, you can save the instance
        pet.save()

        # Redirect or render a success page
        return redirect("/clinic_management_system")
    
    return render(request, "create_pet.html")


# -----------------------------------------------------------------------------WRITE REPORT
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def write_report(request, customer_id, appointment_id):
    customer_user = get_object_or_404(User, pk=customer_id)
    customer = customer_user.customer
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    
    pets = Pet.objects.filter(customer = customer)
    pets_exist = False
    context = { "pets_exist":pets_exist,
                "customer": customer}
    
    if pets:
        pets_exist = True
        context["pets_exist"] = True
        context["pets"] = pets
    
    if request.method == 'POST':
        pet_id = request.POST.get("pet")
        
        pet = get_object_or_404(Pet, pk=pet_id)
        report = request.POST.get("report")
        dose1 = request.POST.get("dose1")
        dose2 = request.POST.get("dose2")
        dose3 = request.POST.get("dose3")
        
        # Create a new PetPreviousReports instance
        report_instance = PetPreviousReports.objects.create(
            pet=pet,
            report=report,
            dose1=dose1,
            dose2=dose2,
            dose3=dose3,
            created_date=timezone.now() 
        )
        report_instance.save()
        appointment.reported = True
        appointment.save()
        
        # Redirect to a success page or any other page
        return redirect('clinic_management_system')
    
    return render(request, "write_report.html", context)


# -----------------------------------------------------------------------------GET PETS OF CUSTOMER
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def pet_history(request):
    if request.method == 'POST':
        customer_phone = request.POST.get("customer_phone")
        customer_user = User.objects.filter(phone_number = customer_phone).first()
        if not customer_user:
            return JsonResponse({'error': 'No Customer with this Number Found!'}, status=400)
        
        customer = customer_user.customer
        pets = Pet.objects.filter(customer = customer)
        pets_exist = True
        if not pets:
            pets_exist = False
            return JsonResponse({'error': "No Pets Found for this Customer"}, status=400)
        
        pets_data = serializers.serialize('python', pets)
        pets_list = [{
            'id': pet['pk'],  # Include pet ID
            **pet['fields']  # Include other fields
        } for pet in pets_data]
        
        customer_data = {
            'id': customer_user.id,
            'name': customer_user.name,
            'email': customer_user.email,
            'phone_number': customer_user.phone_number,
            # Add more fields as needed
        }
        
        context = {
            "pets_exist": pets_exist,
            "body":pets_list,
            "customer": customer_data
            }

        return JsonResponse(context)



# -----------------------------------------------------------------------------GET OLD REPORTS OF PET
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def old_reports(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)
    reports_exist = False
    reports = PetPreviousReports.objects.filter(pet = pet)
    context = {
            "reports_exist": reports_exist}
    if reports:
        reports_exist = True
        pets_data = serializers.serialize('python', reports)
        pets_list = [{
            'id': pet['pk'],  # Include pet ID
            **pet['fields']  # Include other fields
        } for pet in pets_data]
        
        context = {
            "reports_exist": reports_exist,
            "body":pets_list
            }
        
    return JsonResponse(context)



# ! --------------------------------------------------------------------------------------------------FUNCTIONS

# ! -----------------------------------------------------------------------------DOCTOR VERIFICATION
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def verification(request, doctor_id):
    doctor_user = get_object_or_404(User, pk=doctor_id)
    doctor = doctor_user.doctor
    if doctor:
        doctor.is_verified = True
        doctor_user.is_active = True
        os.remove(doctor.certifications.path)
        doctor_user.save()
        doctor.save()
        messages.success(request, f"Dr.{doctor_user.name} is Verified Successfully...")
        return redirect('admin_panel')


# ! -----------------------------------------------------------------------------GET REDIRECT URL
@login_required(login_url='login')
def get_redirect_url(request):
    # Get the stored referrer from session, or default to '/'
    return request.session.get('referrer', '/')


# ! -----------------------------------------------------------------------------DELETE NEWS
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def delete_news(request, news_id):
    news_instance = get_object_or_404(News, pk=news_id)
    os.remove(news_instance.image.path)
    news_instance.delete()
    messages.error(request, "News is Deleted Successfully!")
    return redirect('admin_panel')  


# ! -----------------------------------------------------------------------------CREATE CHAT
@login_required(login_url='login')
@allowed_users(allowed_roles=["Doctors","Customers"])
def make_chat(request, doctor_id):
    doctor = User.objects.filter(id=doctor_id).first().doctor
    
    if request.method == 'POST':
        customer= request.user.customer
        existing_chat = Chat.objects.filter(customer=customer, doctor=doctor).exists()
        if existing_chat:
            return redirect(reverse('chat_details', args=[doctor_id]))
        
        Chat.objects.create(customer = customer, doctor=doctor)
        return redirect(reverse('chat_details', args=[doctor_id]))


# ! -----------------------------------------------------------------------------DELETE ACCOUNT
@login_required(login_url='login')
def delete_account(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.user.groups.filter(name='Admins').exists():
        if request.method == 'POST':
            if hasattr(user, 'doctor'):
                os.remove(user.doctor.profile_photo.path)
            user.delete()
        messages.error(request, f"{user.name}'s Account is Deleted Successfully!")
        return redirect('/admin_panel')
        
    if request.user.groups.filter(name='Customers').exists():
        request.user.delete()
        messages.error(request, f"Your Account is Deleted Successfully!")
        return redirect('/')
    
    if request.user.groups.filter(name='Doctors').exists():
        os.remove(request.user.doctor.profile_photo.path)
        request.user.delete()
        messages.error(request, f"Your Account is Deleted Successfully!")
        return redirect('/')
    
    return redirect('/')


# ! -----------------------------------------------------------------------------UPDATE APPOINTMENT STATUS  
@login_required(login_url='login')
@allowed_users(allowed_roles=["Doctors"])
def update_status(request, appointment_id):

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    appointment = get_object_or_404(Appointment, id=appointment_id)
    new_status = request.POST.get('new_status')
    appointment.status = new_status
    appointment.save()
    doctor = appointment.doctor
    if new_status == 'Done':
        doctor.appointments_count += 1
        doctor.reviews+=1
        doctor.save()


    return JsonResponse({'success': True})  


# ! -----------------------------------------------------------------------------CANCEL APPOINTMENT  
@login_required(login_url='login')
@allowed_users(allowed_roles=["Doctors", "Customers"])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    customer = appointment.customer
    
    if request.user.groups.filter(name='Customers').exists():
        notification_message = f'Your appointment with Dr. {appointment.doctor.user.name} has been canceled.'
        Notification.objects.create(customer=request.user.customer, notification_type='CANCELED', message=notification_message)
    
    if request.user.groups.filter(name='Doctors').exists():
        if not appointment.offline_customer_name:
            notification_message = f'Your appointment with Dr. {appointment.doctor.user.name} has been canceled due to some circumstances.'
            Notification.objects.create(customer=appointment.customer, notification_type='DOCTOR_CANCELED', message=notification_message)
    
    appointment.delete()
    if customer:
        customer.appointments_count -= 1
        customer.save()
    
    if request.user.groups.filter(name='Customers').exists():
        messages.warning(request, f"Your Appointment with Dr. {appointment.doctor.user.name.title()} is Canceled Successfully")
        return redirect("/")
    
    if customer:
        messages.warning(request, f"Your Appointment with {appointment.customer.user.name.title()} on {appointment.date} at {appointment.time} is Canceled Successfully")
    else:
        messages.warning(request, f"Your Appointment with {appointment.offline_customer_name.title()} on {appointment.date} at {appointment.time} is Canceled Successfully")
    return redirect('/clinic_management_system')


# ! -----------------------------------------------------------------------------LOGOUT
@login_required(login_url='login')
def logout(request):
    Logout(request)
    messages.info(request, 'You Logged Out Successfully!')
    return redirect('/')


# ! -----------------------------------------------------------------------------DELETE REVIEW
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def delete_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Feedback, id=review_id)
        print(review) 
        doctor = review.doctor
        doctor.reviews -= 1
        review.delete()
        doctor.save()
    
        return JsonResponse({'success': True})  
        #return redirect('/admin_panel')


# ! -----------------------------------------------------------------------------DELETE SUPPORT TEAM MESSAGE
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def delete_message(request, message_id):
    message = get_object_or_404(SupportTeamMessage, id=message_id)
    message.delete()
    return JsonResponse({"success": True})



# ! -----------------------------------------------------------------------------SEND SUPPORT TEAM RESPONSE
@allowed_users(allowed_roles=["Admins"])
@login_required(login_url='login')
def send_support_team_message(request, message_id):
    message = get_object_or_404(SupportTeamMessage, id=message_id)
    message.response = request.POST.get("response")
    message.answered = True
    message.save()
    return redirect('admin_panel')


# ! -----------------------------------------------------------------------------OFFLINE APPOINTMENT MANAGEMENT
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def offline_appointment(request):
    
    if request.method == 'POST':
        doctor = request.user.doctor
        doctor_price = doctor.price
        doctor_offer_percentage = doctor.offer_percentage
        doctor_offer_price = doctor_price - (doctor_price*doctor_offer_percentage)
        date = request.POST.get('date')
        time = request.POST.get('time')
        offline_customer_name = request.POST.get('offline_customer_name')
        offline_customer_phone = request.POST.get('offline_customer_phone')
    
        Appointment.objects.create(
            doctor=doctor,
            appointment_price=doctor_offer_price,
            date=date,
            time=time,
            offline_customer_name=offline_customer_name,
            offline_customer_phone=offline_customer_phone,
            reported = True,
            
        )
        
        messages.success(request, f"You Successfully Created an Appointment with {offline_customer_name.title()} on {date} at {time}")
        return redirect("clinic_management_system") 


# ! -----------------------------------------------------------------------------CREATE OFFER
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def make_offer(request):
    
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    if request.method == 'POST':
        percentage = request.POST.get('percentage')
        end_date = request.POST.get('end_date')
        doctor = request.user.doctor
        
        doctor.offer_percentage = percentage
        doctor.offer_end_date = end_date
        doctor.save()

        return JsonResponse({'success': True})  


# ! -----------------------------------------------------------------------------DELETE OFFER
@allowed_users(allowed_roles=["Doctors"])
@login_required(login_url='login')
def delete_offer(request):
    doctor = request.user.doctor
    doctor.offer_percentage = float(0.0)
    doctor.offer_end_date = None
    doctor.save()
    return JsonResponse({'success': True})


# ! -----------------------------------------------------------------------------SENDING ACTIVATION Email
@unauthenticated_user
def activate_email(request, user, to_email):
    mail_subject = "Activate your User Account"
    message = render_to_string("activate_email.html", {
        'user': user.email,
        'domain': get_current_site(request).domain,
        'user_id': urlsafe_base64_encode(force_bytes(user.id)),
        'token': account_activation_token.make_token(user),
        'protocol': "https" if request.is_secure() else 'http'
        })
    email =EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Please go to email: {to_email} and click the link')
    else:
        messages.error(request, f'Problem sending email to {to_email}')


# ! -----------------------------------------------------------------------------ACTIVATING EMAIL
@unauthenticated_user
def activate(request, uidb64, token):
    user_id = get_user_model()
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk= user_id)
    except:
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank your for email verification, Now you can login")
        return redirect('login')
    
    else:
        messages.warning(request, "Your Certification is Being Verified!")
        
    return redirect('/')


# ! -----------------------------------------------------------------------------FORGET PASSWORD
@unauthenticated_user
def reset_password_request(request):
    if request.method =='POST':
        email = request.POST.get("email")
        associated_user = get_user_model().objects.filter(Q(email = email)).first()
        if associated_user:
            mail_subject = "Password Reset Request"
            message = render_to_string("forget_password_email.html", {
                'user': associated_user.email,
                'domain': get_current_site(request).domain,
                'user_id': urlsafe_base64_encode(force_bytes(associated_user.id)),
                'token': account_activation_token.make_token(associated_user),
                'protocol': "https" if request.is_secure() else 'http'
                })
            email = EmailMessage(mail_subject, message, to=[associated_user.email])
            if email.send():
                messages.success(request, """ Password reset Sent to Email """)
                return redirect('/')
            else:
                messages.error(request, "Email Doesn't Exist Go to SignUp")
            
        else:
            messages.error(request, "Email Doesn't Exist Go to SignUp")
            return redirect('/')
            
    return render(
        request=request,
        template_name="reset_password.html"
    )


# ! -----------------------------------------------------------------------------PASSWORD RESET
@unauthenticated_user
def passwordResetConfirm(request, uidb64, token):
    user_id = get_user_model()
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk= user_id)
        
    except:
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            
            hashed_password = make_password(password)
            user.password = hashed_password
            user.save()
            messages.success(request, "Your Password is Changed Successfully!")
            return redirect('login')
            
        return render(request, 'forget_password.html')
    
    else:
        messages.error(request, "Link is Expired!")
    
    messages.error(request,"Something went wrong, redirecting to home page!")
    return redirect('/')


# ! -----------------------------------------------------------------------------MARK NOTIFICATION AS READ
@allowed_users(allowed_roles=["Customers"])
@login_required(login_url='login')
def mark_notification_as_read(request, notification_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})  


# ! -----------------------------------------------------------------------------CALCULATE DAYS UNTIL APPOINTMENT
def days_until_appointment(appointment_date_str):
    return (datetime.strptime(appointment_date_str, '%A %m/%d').date().replace(year=datetime.now().year) - datetime.now().date()).days

