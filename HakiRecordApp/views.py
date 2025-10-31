from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib import colors
from  .models import *
from .sms_utils import send_sms_message
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os
from reportlab.lib.utils import ImageReader
from django.db.models import Q





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
        incident_evidence = request.FILES.get('incident_evidence')

        # Save the statement
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


        sms_message = (
            f"Hello {first_name}, your case has been recorded successfully.\n\n"
            f"Occurrence No: {statement.ob_number}\n"
            f"Statement: {incident_description}\n"
            f"Thank you for reporting via HakiRecord."
        )

        # Send SMS
        send_sms_message(phone_number, sms_message)
        # --- SMS section ends here ---

        messages.success(request, "Statement recorded successfully and SMS sent!")
        return redirect('statement')

    return render(request, 'statement.html')


def login_fn(request):
    if request.method == 'POST':
        service_number = request.POST['service_number']
        login_password = request.POST['login_password']
        user = authenticate(request, username=service_number, password=login_password)
        if user is not None:
            login(request, user)
            return redirect('login_success')

        else:
            messages.error(request, 'Invalid service number or password. Please try again.')

    return render(request,'login.html')


def logout_view(request):
    logout(request)
    return redirect('homepage')


@login_required(login_url='login')
def view_cases(request):
    query = request.GET.get('q')  # Get the search query from URL parameter
    if query:
        statements = Statement.objects.filter(
            Q(ob_number__icontains=query) |
            Q(incident_type__icontains=query) |
            Q(id_number__icontains=query)
        )
    else:
        statements = Statement.objects.all()

    return render(request, "view_statements.html", {"statements": statements, "query": query})


def case_detail(request, pk):
    statement = get_object_or_404(Statement, pk=pk)
    return render(request, 'case_details.html', {'statement': statement})

def generate_case_pdf(request, pk):
    statement = get_object_or_404(Statement, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Case_{statement.ob_number}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    x_margin = 50

    #  Light yellow background
    p.setFillColorRGB(1, 1, 0.85)
    p.rect(0, 0, width, height, fill=True, stroke=False)
    p.setFillColor(colors.black)

    #  Logo
    logo_path = os.path.join(settings.BASE_DIR, 'HakiRecordApp', 'static', 'images', 'logo1.png')
    if os.path.exists(logo_path):
        logo_width = 120
        logo_height = 70
        logo_x = (width - logo_width) / 2
        logo_y = height - logo_height - 40
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
    else:
        print(f"Logo not found at: {logo_path}")

    # Title
    y_position = height - 150
    p.setTitle(f"Case Report - {statement.ob_number}")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y_position, "HakiRecord Case Report")

    y_position -= 40
    p.setFont("Helvetica", 12)

    #  Case fields
    fields = [
        ("OB Number", statement.ob_number),
        ("Officer Service No.", statement.service_no.username),
        ("Last Name", statement.last_name),
        ("ID Number", statement.id_number),
        ("Incident Date", str(statement.incident_date)),
        ("Incident Type", statement.incident_type),
        ("Incident Location", statement.incident_location),
        ("Date Recorded", statement.recorded_at.strftime("%B %d, %Y")),
    ]

    for label, value in fields:
        if y_position < 80:
            p.showPage()
            p.setFillColorRGB(1, 1, 0.85)
            p.rect(0, 0, width, height, fill=True, stroke=False)
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 12)
            y_position = height - 80

        p.drawString(x_margin, y_position, f"{label}:")
        text = p.beginText(x_margin + 150, y_position)
        text.textLines(str(value))
        p.drawText(text)
        y_position -= 30

    #  Case description
    if y_position < 150:
        p.showPage()
        p.setFillColorRGB(1, 1, 0.85)
        p.rect(0, 0, width, height, fill=True, stroke=False)
        p.setFillColor(colors.black)
        y_position = height - 80

    p.setFont("Helvetica-Bold", 12)
    p.drawString(x_margin, y_position, "Description:")
    y_position -= 20

    p.setFont("Helvetica", 11)
    text = p.beginText(x_margin, y_position)
    text.textLines(statement.incident_description)
    p.drawText(text)

    # ✅ Evidence section (after all text)
    if statement.incident_evidence:
        evidence_path = os.path.join(settings.MEDIA_ROOT, str(statement.incident_evidence))

        p.showPage()  # start new page
        p.setFillColorRGB(1, 1, 0.85)
        p.rect(0, 0, width, height, fill=True, stroke=False)
        p.setFillColor(colors.black)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(x_margin, height - 80, "Attached Evidence")

        if evidence_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = ImageReader(evidence_path)
                p.drawImage(img, x_margin, height / 3, width=width - 2 * x_margin, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                p.setFont("Helvetica", 11)
                p.drawString(x_margin, height / 2, f"Error displaying image: {str(e)}")

        elif evidence_path.lower().endswith('.pdf'):
            p.setFont("Helvetica", 11)
            p.drawString(x_margin, height - 120, "Evidence is a PDF document.")
        else:
            p.setFont("Helvetica", 11)
            p.drawString(x_margin, height - 120, "Unsupported file type.")

    #  Save PDF
    p.save()
    return response

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



def crime_analysis(request):
    try:
        # Use the Statement model instead of Crime
        statements = Statement.objects.exclude(incident_date__isnull=True)

        # Group crimes by month
        crimes_by_date = (
            statements
            .annotate(period=TruncMonth('incident_date'))
            .values('period')
            .annotate(count=Count('id'))
            .order_by('period')
        )

        # Group crimes by incident type
        crimes_by_type = (
            statements
            .values('incident_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Send JSON data to the template
        context = {
            'crimes_by_date': json.dumps(list(crimes_by_date), default=str),
            'crimes_by_type': json.dumps(list(crimes_by_type)),
        }

        return render(request, 'crime_analysis.html', context)

    except Exception as e:
        print("Error in crime_analysis:", e)
        return render(request, 'crime_analysis.html', {
            'crimes_by_date': json.dumps([]),
            'crimes_by_type': json.dumps([]),
            'error_message': str(e)
        })

