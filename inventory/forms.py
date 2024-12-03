from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomSignupForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
        strip=False,
        required=True,
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, required=True, widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        if commit:
            user.save()
        return user
