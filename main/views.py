from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from .models import *
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .forms import *


# Reset password form
@login_required
def reset_password(request):
    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("password_change_done")  # Redirect to success page
    else:
        form = SetPasswordForm(request.user)

    return render(request, "password_change.html", {"form": form})



#For login and logout logic
def custom_logout(request):
    logout(request)
    return redirect('login')


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('agent:dashboard') if request.user.is_staff else redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        user = None

        # Check if identifier is an email or username
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('agent:agent_user_list') if user.is_staff else redirect('index')
        else:
            messages.error(request, "Invalid username/email or password")

    return render(request, 'login.html')


@login_required(login_url='login')
@csrf_exempt
def index(request):
    if request.method == "GET" and "domain" in request.GET:
        domain = request.GET.get("domain", "").strip()
        if not domain:
            return JsonResponse({"error": "Domain is required"}, status=400)

        # Domainr API URL (No API key required)
        api_url = f"https://api.domainr.com/v2/status?domain={domain}&mashape-key=free"

        try:
            response = requests.get(api_url)
            data = response.json()

            # Debugging: Print response
            print("Domainr API Response:", data)

            if response.status_code == 200 and "status" in data:
                availability = data["status"][0]["status"]

                # Check if the domain is available
                available = availability in ["inactive", "undelegated", "available"]

                return JsonResponse({"domain": domain, "available": available})
            else:
                return JsonResponse({"error": "Invalid response from API", "details": data}, status=500)

        except requests.RequestException as e:
            return JsonResponse({"error": "API request failed", "details": str(e)}, status=500)

    return render(request, "index.html")


# USer Profile settings
@login_required(login_url='login')
def user_profile(request):
    """Display user details with an option to edit."""
    return render(request, 'profile.html', {'user': request.user})



@login_required(login_url='login')
def edit_profile(request):
    """Allow users to update their profile information."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})



@login_required(login_url='login')
def invoice_page(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    additional_charges = invoice.additional_charges.all()
    
    context = {
        "invoice": invoice,
        "additional_charges": additional_charges,
        "total_amount": invoice.price + sum(charge.amount for charge in additional_charges),
    }
    return render(request, "invoice.html", context)



@login_required(login_url='login')
def invoice_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '').lower()
    date_filter = request.GET.get('date', '')

    # Filter invoices only for the logged-in user
    invoices = Invoice.objects.filter(user=request.user)

    if search_query:
        invoices = invoices.filter(
            Q(id__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(payment_status=status_filter)

    if date_filter:
        invoices = invoices.filter(due_date=date_filter)

    context = {
        'invoices': invoices,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'invoice_list.html', context)



# This is for the HTML to PDF
import pdfcrowd
from django.http import HttpResponse
from django.template.loader import render_to_string


@login_required(login_url='login')
def generate_invoice_pdf(request, invoice_id):
    # Fetch the invoice data
    invoice = Invoice.objects.get(id=invoice_id)
    additional_charges = invoice.additional_charges.all()
    
    # Prepare context
    context = {
        "invoice": invoice,
        "additional_charges": additional_charges,
        "total_amount": invoice.price + sum(c.amount for c in additional_charges),
    }

    # Render the HTML template
    html_content = render_to_string("invoice_pdf.html", context)

    try:
        # Initialize PDFCrowd API Client
        client = pdfcrowd.HtmlToPdfClient("datpocketguy", "eadeba87ba00f79872500e5aff386dc4")
        
        # Generate PDF from HTML
        pdf_bytes = client.convertString(html_content)

        # Create HTTP response with PDF
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        return response

    except pdfcrowd.Error as e:
        return HttpResponse(f"PDF generation failed: {e}", status=500)


