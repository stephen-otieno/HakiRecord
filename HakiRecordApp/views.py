from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from  .models import *


def index(request):
    return render(request, "index.html")

@login_required(login_url='login')
def record_statement(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        id_number = request.POST["id_number"]
        dob = request.POST["dob"]
        address = request.POST["address"]
        phone_number = request.POST["phone_number"]
        incident_type = request.POST["incident_type"]
        incident_location = request.POST["incident_location"]
        incident_date = request.POST["incident_date"]
        incident_time = request.POST["incident_time"]
        suspect_description = request.POST["suspect_description"]
        incident_description = request.POST["incident_description"]
        incident_evidence = request.FILES.getlist('incident_evidence')[0] if request.FILES.getlist('incident_evidence') else None

        statement = Statement(
            service_no=request.user,
            first_name=first_name,
            last_name=last_name,
            id_number=id_number,
            dob=dob,
            address=address,
            phone_number=phone_number,
            incident_type=incident_type,
            incident_location=incident_location,
            incident_date=incident_date,
            incident_time=incident_time,
            suspect_description=suspect_description,
            incident_description=incident_description,
            incident_evidence=incident_evidence,

        )

        statement.save()


    return render(request, 'statement.html')



def login_fn(request):
    if request.method == "POST":
        service_number = request.POST["service_number"]
        login_password = request.POST["login_password"]
        user = authenticate(request,username= service_number,password=login_password)
        if user is not None:
            return redirect('login_success')
        else:
            messages.error(request, "Invalid service number or password.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('homepage')

@login_required(login_url='login')
def view_cases(request):
    statements = Statement.objects.all()
    return render(request, "view_statements.html", {"statements": statements})


def recent_actions(request):
    # Fetch recent 20 admin actions
    actions = LogEntry.objects.select_related('content_type', 'user').order_by('-action_time')
    return render(request, 'recent_actions.html', {'actions': actions})


def contact(request):
    if request.method == "POST":
        contact_name = request.POST["contact_name"]
        contact_email = request.POST["contact_email"]
        contact_message = request.POST["contact_message"]

        contacts = Contact(
            contact_name=contact_name,
            contact_email=contact_email,
            contact_message=contact_message,
        )
        contacts.save()
    return render(request, 'contact.html')

def evidence_vault(request):
    statements = Statement.objects.all().order_by('-id')
    return render(request, 'evidence.html',{"statements": statements})

def shift_allocation(request):
    return render(request, 'shift_allocation.html')

def login_success(request):
    return render(request, 'login_success.html')

