from django.db.models import Count
from .models import Invoice

def invoice_status_counts(request):
    if not request.user.is_authenticated:
        return {}  # Return empty if the user is not logged in

    # Filter invoices for the logged-in user
    status_counts = Invoice.objects.filter(user=request.user).values('payment_status').annotate(count=Count('id'))

    # Convert to a dictionary with lowercase keys
    status_count_dict = {item['payment_status'].lower(): item['count'] for item in status_counts}

    return {
        'paid_count': status_count_dict.get('paid', 0),
        'unpaid_count': status_count_dict.get('unpaid', 0),
        'cancelled_count': status_count_dict.get('cancelled', 0),
        'refunded_count': status_count_dict.get('refunded', 0),
    }
