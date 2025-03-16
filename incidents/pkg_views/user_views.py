from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""
    
    # Add a confirmation field for username changes
    confirm_username_change = forms.BooleanField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'confirm_username_change']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
        }
    
    def clean_username(self):
        """Validate that the username is unique and confirm changes."""
        username = self.cleaned_data.get('username')
        instance = getattr(self, 'instance', None)
        
        # If username is being changed, make sure it's not taken and change is confirmed
        if instance and instance.username != username:
            if User.objects.filter(username=username).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(_("This username is already used."))
            
            # If username change isn't confirmed via modal, raise error
            if not self.cleaned_data.get('confirm_username_change'):
                raise forms.ValidationError(_("You must confirm the username change via the confirmation window."))
                
        return username


@login_required
def profile(request):
    """
    View for displaying and updating user profile information.
    
    This view handles both:
    - GET requests to display the user's profile
    - POST requests to update profile information or change password
    
    The form submission is differentiated by the presence of a 'form_type'
    parameter in the POST data.
    """
    user = request.user
    profile_form = UserProfileForm(instance=user)
    password_form = PasswordChangeForm(user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Handle profile info update
        if form_type == 'profile':
            profile_form = UserProfileForm(request.POST, instance=user)
            
            # Check if username is changing for custom message
            original_username = user.username
            new_username = request.POST.get('username')
            username_changed = original_username != new_username
            
            if profile_form.is_valid():
                profile_form.save()
                if username_changed:
                    messages.success(request, f"_('Your username was changed from') {original_username} _('to') {new_username}.")
                else:
                    messages.success(request, "_('Your profile information was updated successfully.')")
                return redirect('user_profile')
        
        # Handle password change
        elif form_type == 'password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                updated_user = password_form.save()
                # Important: update the session to prevent logout
                update_session_auth_hash(request, updated_user)
                messages.success(request, "_('Your password was changed successfully.')")
                return redirect('user_profile')
    
    # Get statistics about user's incidents
    user_stats = {
        'created_incidents': user.created_incidents.count(),
        'assigned_incidents': user.assigned_incidents.count(),
        'open_assigned': user.assigned_incidents.filter(status='new').count(),
        'in_progress_assigned': user.assigned_incidents.filter(status='in_progress').count(),
        'resolved_assigned': user.assigned_incidents.filter(status='resolved').count(),
    }
    
    # Get the user's recent incidents
    recent_created = user.created_incidents.order_by('-created_at')[:5]
    recent_assigned = user.assigned_incidents.order_by('-updated_at')[:5]
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_stats': user_stats,
        'recent_created': recent_created,
        'recent_assigned': recent_assigned,
    }
    
    return render(request, 'incidents/user_profile.html', context)
