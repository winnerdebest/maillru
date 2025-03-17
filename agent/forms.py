from django import forms
from main.models import *

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['product_type', 'product_name', 'price', 'transaction_date', 'due_date', 'payment_gateway', 'payment_status']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'border rounded p-2 w-full'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'border rounded p-2 w-full'}),
            'product_type': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'payment_gateway': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'payment_status': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'product_name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full', 'placeholder': 'Enter product name'}),
            'price': forms.NumberInput(attrs={'class': 'border rounded p-2 w-full', 'min': '0'}),
        }


# For Creating new users
class UserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash password
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        return user
