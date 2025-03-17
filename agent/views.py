from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import *
from main.models import *


# Filter for only staff to login to this view 

def is_staff_user(user):
    return user.is_authenticated and user.is_staff 


@login_required(login_url='login')
@user_passes_test(is_staff_user)
def agent_user_list(request):
    """Displays a paginated list of users (excluding superusers and staff) with search and sorting functionality."""

    query = request.GET.get('q', '')  # Get search query
    sort_by = request.GET.get('sort', 'name')  # Get sorting parameter
    order = request.GET.get('order', 'asc')  # Get sort order (asc/desc)

    # Define sorting options
    sort_options = {
        'name': 'first_name',
        'email': 'email',
        'date_joined': 'date_joined'
    }
    
    # Apply sorting and order
    sort_field = sort_options.get(sort_by, 'first_name')
    if order == 'desc':
        sort_field = f'-{sort_field}'

    # Filter users (exclude superusers and staff)
    users = User.objects.filter(
        is_superuser=False,
        is_staff=False
    ).filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).order_by(sort_field).select_related('profile')

    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)

    return render(request, 'agent/dashboard.html', {
        'users': page_users,
        'query': query,
        'sort_by': sort_by,
        'order': order,
        'sort_options': sort_options  # Pass sorting options to template
    })


# For the User Invoice
@login_required(login_url='login')
@user_passes_test(is_staff_user)
def user_invoice_list(request, user_id):
    """Displays a user's profile details and paginated invoices with search functionality."""
    
    user = get_object_or_404(User, id=user_id)
    
    query = request.GET.get('q', '')  # Search query
    sort_by = request.GET.get('sort', 'transaction_date')  # Default sorting by transaction date
    order = request.GET.get('order', 'desc')  # Default descending order

    # Sorting options
    sort_options = {
        'transaction_date': 'transaction_date',
        'due_date': 'due_date',
        'price': 'price',
        'status': 'payment_status'
    }

    sort_field = sort_options.get(sort_by, 'transaction_date')
    if order == 'desc':
        sort_field = f'-{sort_field}'

    # Filter invoices by user and search query
    invoices = Invoice.objects.filter(
        user=user
    ).filter(
        Q(product_name__icontains=query) | 
        Q(id__icontains=query)
    ).order_by(sort_field)

    # Pagination
    paginator = Paginator(invoices, 10)  # Show 10 invoices per page
    page_number = request.GET.get('page')
    page_invoices = paginator.get_page(page_number)

    return render(request, 'agent/user_invoice_list.html', {
        'user': user,
        'invoices': page_invoices,
        'query': query,
        'sort_by': sort_by,
        'order': order,
        'sort_options': sort_options
    })



# For Invoice Creation
@login_required(login_url='login')
@user_passes_test(is_staff_user)
def add_invoice(request, user_id):
    viewed_user = get_object_or_404(User, id=user_id)  # Get the user we are adding an invoice for

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = viewed_user  # Attach invoice to the specified user
            invoice.save()
            return redirect('agent:user_invoice_list', user_id=user_id)  # Redirect to user's invoices
    else:
        form = InvoiceForm()

    return render(request, 'agent/add_invoice.html', {'form': form, 'viewed_user': viewed_user})



# This is for editing the invoice
@login_required(login_url='login')
@user_passes_test(is_staff_user)
def edit_invoice(request, user_id, invoice_id):
    """Allows editing an existing invoice for a specific user."""
    
    invoice = get_object_or_404(Invoice, id=invoice_id, user_id=user_id)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('agent:user_invoice_list', user_id=user_id)  # Redirect to user's invoices
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, 'agent/edit_invoice.html', {
        'form': form,
        'invoice': invoice,
        'user_id': user_id
    })




# This is for the password reset
@login_required(login_url='login')
@user_passes_test(is_staff_user)
def change_user_password(request, user_id):
    """Allows an agent to change a user's password."""
    
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.password = make_password(new_password)  # Hash password
            user.save()
            messages.success(request, f"Password for {user.username} has been updated.")
            return redirect('agent:user_invoice_list', user_id=user.id)

    return render(request, 'agent/change_password.html', {'user': user})



@login_required(login_url='login')
@user_passes_test(is_staff_user)
def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('agent:agent_user_list')  # Redirect to user list
        else:
            messages.error(request, "Error creating user. Please check the form.")
    else:
        form = UserCreationForm()

    return render(request, "agent/create_user.html", {"form": form})