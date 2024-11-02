from django import forms
from .models import Contact,CustomUser,Rating
from django.contrib.auth.forms import UserCreationForm


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Add a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')  # Only ask for username, email, and passwords
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 150:
            raise forms.ValidationError("Username must be 150 characters or fewer.")
        if not username.isalnum() and not any(char in ['@', '.', '+', '-', '_'] for char in username):
            raise forms.ValidationError("Username can only contain letters, digits, and @/./+/-/_ characters.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        # Additional email validation can be added here if needed
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # Replace with your actual user model
        fields = ['username', 'email', 'location', 'age', 'image_url']  # Specify fields to update

    # Optionally, you can add custom validation if needed
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 0 or rating > 10:
            raise forms.ValidationError("Rating must be between 0 and 10.")
        return rating