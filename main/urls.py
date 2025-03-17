from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoice/<int:invoice_id>/', invoice_page, name='invoice_page'),
    path('invoice/<int:invoice_id>/download/', generate_invoice_pdf, name='download_invoice'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
