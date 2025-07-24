from django.conf import settings
from django.shortcuts import render , redirect , get_object_or_404 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from .forms import LoginForm , RegistrationForm , PasswordResetForm , usernameRecoveryForm, AccountDeletionForm, AccountDeletionConfirmationForm 
from .utility import get_jwt_tokens


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages


from django.utils import timezone
import json
import requests
import uuid
from django.conf import settings
from .models import UserProfile


def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'core/dashboard.html')
    else:
        return redirect('home')
    

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data['remember_me']

        user = authenticate(request, username=username, password=password)
        if user:
            user_profile = UserProfile.objects.filter(user=user).first()
            if not user_profile or not user_profile.email_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return render(request, 'authen/login.html', {'form': form})

            login(request, user)

            request.session.set_expiry(1209600 if remember_me else 0)

            tokens = get_jwt_tokens(username, password)
            if tokens:
                request.session['access_token'] = tokens['access']
                request.session['refresh_token'] = tokens['refresh']

            messages.success(request, 'Login successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'authen/login.html', {'form': form})


def register_view(request): 
    if request.user.is_authenticated:
        return redirect('dashboard') 
    
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            first_name = request.POST.get('first_name', '')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Check if user already exists in database (these are activated users)
            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists. Please choose a different username.')
                else:
                    messages.error(request, 'Email already exists. Please use a different email.')
                return render(request, 'authen/register.html', {'form': form})
              # Store registration data ONLY in session (no database save)
            registration_data = {
                'first_name': first_name,
                'username': username,
                'email': email,
                'password': password,
                'timestamp': timezone.now().isoformat()
            }
            
            # Create a temporary token for activation
            import uuid
            temp_token = uuid.uuid4().hex
            request.session[f'pending_registration_{temp_token}'] = registration_data
            
            # Create activation URL
            activation_url = f"http://142.93.168.121/activate-registration/{temp_token}/"
            # Send simple activation email using Django's send_mail
            subject = 'Activate Your OptiChoice Account'
            name_to_use = first_name if first_name else username
            message = f"""Hi {name_to_use},

Thank you for joining OptiChoice! To complete your registration, please click the link below:

{activation_url}

This link will expire in 24 hours for security.

Best regards,
The OptiChoice Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                print(f"Email sent successfully to {email}")  # Debug log
                
                messages.success(
                    request,
                    'Registration link sent! Please check your email to activate your account. No account has been created yet.'
                )
            except Exception as email_error:
                print(f"Email sending failed: {email_error}")  # Debug log
                print(f"Email settings - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}")
                print(f"Email settings - TLS: {settings.EMAIL_USE_TLS}, User: {settings.EMAIL_HOST_USER}")
                messages.error(
                    request,
                    f'Registration failed: Unable to send activation email. Please try again later. Error: {str(email_error)}'
                )
                return render(request, 'authen/register.html', {'form': form})
            return redirect('register')
            
        except Exception as e:
            print(f"Registration error: {e}")
            messages.error(request, f'Registration failed: {str(e)}')

    return render(request, 'authen/register.html' , {'form': form})


def activate_registration(request, temp_token):
    """Handle activation of pending registration using temporary token."""
    try:
        session_key = f'pending_registration_{temp_token}'
        registration_data = request.session.get(session_key)
        
        if not registration_data:
            messages.error(request, 'Invalid or expired activation link.')
            return redirect('register')
        
        # Check if link has expired (24 hours)
        timestamp_str = registration_data.get('timestamp')
        if timestamp_str:
            timestamp = timezone.datetime.fromisoformat(timestamp_str)
            if timezone.now() - timestamp > timezone.timedelta(hours=24):                # Clean up expired session data
                del request.session[session_key]
                messages.error(request, 'Activation link has expired. Please register again.')
                return redirect('register')
        
        # Check if user already exists (final check before creation)
        username = registration_data['username']
        email = registration_data['email']
        password = registration_data['password']
        first_name = registration_data.get('first_name', '')
        
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            # Clean up session data
            del request.session[session_key]
            messages.error(request, 'User with this username or email already exists.')
            return redirect('register')
        
        # Create the user account now
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            is_active=True  # Immediately active since they clicked the link
        )
        
        # Create user profile
        user_profile = UserProfile.objects.create(
            user=user,
            email_verified=True,
            email_verification_sent_at=timezone.now()
        )
        
        # Clean up session data
        del request.session[session_key]
          # Send confirmation email
        try:
            name_to_use = first_name if first_name else username
            send_mail(
                'Welcome to OptiChoice!',
                f'Hi {name_to_use},\n\nYour account has been successfully activated! You can now log in and start using OptiChoice.\n\nBest regards,\nThe OptiChoice Team',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending confirmation email: {e}")
        
        messages.success(request, 'Your account has been activated successfully! You can now log in.')
        return redirect('login')
        
    except Exception as e:
        print(f"Activation error: {e}")
        messages.error(request, 'An error occurred during activation. Please try registering again.')
        return redirect('register')



@login_required 
def logout_view(request):
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token'] 

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dashboard') 



def forgot_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Update timestamp for password reset request
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                user_profile.password_reset_sent_at = timezone.now()
                user_profile.save()
                
                # Create password reset URL using Django's built-in token generator
                reset_url = f"http://142.93.168.121/password-reset-confirm/{user.pk}/{default_token_generator.make_token(user)}/"
                
                # Send simple password reset email
                subject = 'Reset Your OptiChoice Password'
                message = f"""Hi {user.username},

We received a request to reset your password for your OptiChoice account.

Click the link below to reset your password:

{reset_url}

This link will expire in 24 hours for security.

If you didn't request this password reset, please ignore this email.

Best regards,
The OptiChoice Team"""
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
            except User.DoesNotExist:
                pass
            except Exception as e:
                print(f"Password reset error: {e}")
                messages.error(request, 'An error occurred. Please try again.')
                return render(request, 'authen/password_reset.html', {'form': form})
            
            messages.success(request, 
                'If an account with that email exists, password reset instructions have been sent.')
            return redirect('login')

    else:
        form = PasswordResetForm()

    return render(request, 'authen/password_reset.html', {'form': form})


def reset_password_confirmation_view(request, uid, token):
    try:
        user = get_object_or_404(User, pk=uid)

        # Verify Django's built-in token (this handles expiration automatically)
        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid or expired password reset link.')
            return redirect('forgot_password')
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'authen/password_reset_confirmation.html', {'uid': uid, 'token': token})
            
            if not password or len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'authen/password_reset_confirmation.html', {'uid': uid, 'token': token})            # Set new password and save user
            user.set_password(password)
            user.save()

            # Clear reset timestamp
            user_profile.password_reset_sent_at = None
            user_profile.save()

            # Send simple confirmation email
            try:
                send_mail(
                    'Password Changed Successfully',
                    f'Hi {user.username},\n\nYour password has been successfully changed.\n\nIf you did not make this change, please contact support immediately.\n\nBest regards,\nThe OptiChoice Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending password change confirmation: {e}")

            messages.success(request, 'Your password has been reset successfully. You can now log in.')
            return redirect('login')
        
        return render(request, 'authen/password_reset_confirmation.html', {'uid': uid, 'token': token})

    except Exception as e:
        print(f"Password reset confirm error: {e}")
        messages.error(request, 'Invalid password reset link.')
        return redirect('forgot_password')
    





        
def forgot_username_view(request):
    if request.method == 'POST':
        form = usernameRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                
                # Update timestamp for username reset request
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                user_profile.password_reset_sent_at = timezone.now()
                user_profile.save()
                
                # Create username reminder URL
                reminder_url = f"http://142.93.168.121/reset_username_confirmation_view/{user.pk}/{default_token_generator.make_token(user)}/"
                
                # Send simple username reminder email
                subject = 'Your OptiChoice Username'
                message = f"""Hi there,

We received a request for your username reminder.

Your username is: {user.username}

Click this link to confirm this action:
{reminder_url}

If you didn't request this, please ignore this email.

Best regards,
The OptiChoice Team"""
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
            except User.DoesNotExist:
                pass
            except Exception as e:
                print(f"Username reminder error: {e}")
                messages.error(request, 'An error occurred. Please try again.')
                return render(request, 'authen/forgot_username.html', {'form': form})
            
            messages.success(request, 
                'If an account with that email exists, username reminder instructions have been sent.')
            return redirect('login')

    else:
        form = usernameRecoveryForm()

    return render(request, 'authen/forgot_username.html', {'form': form})



def reset_username_confirmation_view(request, uid, token):
    try:
        user = get_object_or_404(User, pk=uid)

        # Verify token
        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid or expired username reminder link.')
            return redirect('forgot_username')

        # Check token validity in user profile
        try:
            user_profile = UserProfile.objects.get(user=user)
            if not user_profile.is_password_reset_valid():  # or is_username_reset_valid() if separate
                messages.error(request, 'Username reminder link has expired.')
                return redirect('forgot_username')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid username reminder link.')
            return redirect('forgot_username')        # Clear timestamp now that it has been used
        user_profile.password_reset_sent_at = None
        user_profile.save()

        # Simply show the user their username
        return render(request, 'authen/show_username.html', {'username': user.username})

    except Exception as e:
        print(f"Username reminder error: {e}")
        messages.error(request, 'Invalid username reminder link.')
        return redirect('forgot_username')


def home_view(request):
    return render(request, 'core/landing.html')





def about_view(request):
    return render(request, 'core/about.html')


@login_required
def profile_view(request):
    return render(request, 'core/profile.html')


@login_required
def delete_account_view(request):
    """Handle account deletion request with email confirmation."""
    if request.method == 'POST':
        form = AccountDeletionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                user = request.user
                
                # Update timestamp for account deletion request
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                user_profile.account_deletion_sent_at = timezone.now()
                user_profile.save()
                
                # Create account deletion confirmation URL
                deletion_url = f"http://142.93.168.121/delete-account-confirm/{user.pk}/{default_token_generator.make_token(user)}/"
                
                # Send account deletion confirmation email
                subject = 'Confirm Account Deletion - OptiChoice'
                message = f"""Hi {user.username},

We received a request to delete your OptiChoice account.

⚠️ WARNING: This action cannot be undone! ⚠️

If you proceed, the following data will be permanently deleted:
• Your profile information
• All saved recommendations
• Your activity history
• Personal preferences
• All associated data

Click the link below to confirm account deletion:

{deletion_url}

This link will expire in 1 hour for security.

If you did not request this account deletion, please ignore this email and your account will remain active.

Need help? Contact our support team.

Best regards,
The OptiChoice Team"""
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                messages.success(request, 
                    'Account deletion confirmation email has been sent to your email address. Please check your inbox.')
                return redirect('profile')
                
            except Exception as e:
                print(f"Account deletion request error: {e}")
                messages.error(request, 'An error occurred. Please try again.')
                return render(request, 'authen/delete_account.html', {'form': form})
    
    else:
        form = AccountDeletionForm(user=request.user)
    
    return render(request, 'authen/delete_account.html', {'form': form})


@login_required
def delete_account_confirm_view(request, uid, token):
    """Handle account deletion confirmation."""
    try:
        user = get_object_or_404(User, pk=uid)
        
        # Verify user is the current logged-in user
        if user != request.user:
            messages.error(request, 'You can only delete your own account.')
            return redirect('profile')

        # Verify Django's built-in token (this handles expiration automatically)
        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid or expired account deletion link.')
            return redirect('profile')
        
        # Get user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Check if the deletion request is still valid (within 1 hour)
        if not user_profile.is_account_deletion_valid():
            messages.error(request, 'Account deletion request has expired. Please try again.')
            return redirect('profile')

        if request.method == 'POST':
            form = AccountDeletionConfirmationForm(request.POST)
            if form.is_valid():
                try:
                    username = user.username
                    user_email = user.email
                    
                    # Clear deletion timestamp
                    user_profile.account_deletion_sent_at = None
                    user_profile.save()
                    
                    # Send final confirmation email before deletion
                    subject = 'OptiChoice Account Deleted'
                    message = f"""Hi {username},

Your OptiChoice account has been successfully deleted.

All your data including:
• Profile information
• Saved recommendations
• Activity history
• Personal preferences

has been permanently removed from our systems.

Thank you for being part of OptiChoice. We're sorry to see you go.

Best regards,
The OptiChoice Team"""
                    
                    # Send email before deleting user
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email],
                        fail_silently=True,  # Don't fail if email doesn't send
                    )
                    
                    # Log out the user first
                    logout(request)
                    
                    # Delete the user (this also deletes the related UserProfile due to CASCADE)
                    user.delete()
                    
                    # Show success message and redirect to home
                    messages.success(
                        request, 
                        f'Account "{username}" has been permanently deleted. We\'re sorry to see you go!'
                    )
                    return redirect('home')
                    
                except Exception as e:
                    print(f"Account deletion confirmation error: {e}")
                    messages.error(request, 'An error occurred while deleting your account. Please try again.')
                    return render(request, 'authen/delete_account_confirm.html', {'uid': uid, 'token': token, 'form': form})
        
        else:
            form = AccountDeletionConfirmationForm()
        
        return render(request, 'authen/delete_account_confirm.html', {'uid': uid, 'token': token, 'form': form})
        
    except Exception as e:
        print(f"Account deletion confirmation error: {e}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('profile')




















