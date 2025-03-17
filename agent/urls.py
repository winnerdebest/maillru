from django.urls import path
from .views import *

app_name = 'agent'

urlpatterns = [
     path('users/', agent_user_list, name='agent_user_list'),
     path('users/<int:user_id>/invoices/', user_invoice_list, name='user_invoice_list'),
     path('users/<int:user_id>/invoices/add/', add_invoice, name='add_invoice'),
     path('user/<int:user_id>/invoice/<str:invoice_id>/edit/', edit_invoice, name='edit_invoice'),
     path('users/<int:user_id>/change-password/', change_user_password, name='change_user_password'),
     path("create-user/", create_user, name="create_user"),
]
