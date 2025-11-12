# Authentication & Utility Pages Documentation

Complete guide for using Skote Authentication and Utility page templates in your Django project.

---

## Table of Contents

1. [Authentication Pages](#authentication-pages)
   - [Login Pages](#login-pages)
   - [Register Pages](#register-pages)
   - [Password Reset Pages](#password-reset-pages)
   - [Lock Screen Pages](#lock-screen-pages)
   - [Email Confirmation Pages](#email-confirmation-pages)
   - [Email Verification Pages](#email-verification-pages)
   - [Two-Step Verification Pages](#two-step-verification-pages)

2. [Utility Pages](#utility-pages)
   - [Starter Page](#starter-page)
   - [Maintenance Page](#maintenance-page)
   - [Coming Soon Page](#coming-soon-page)
   - [Timeline Page](#timeline-page)
   - [FAQs Page](#faqs-page)
   - [Pricing Page](#pricing-page)
   - [Error Pages (404, 500)](#error-pages)

3. [URL Configuration](#url-configuration)
4. [View Examples](#view-examples)
5. [Customization Guide](#customization-guide)

---

## Authentication Pages

All authentication pages are standalone templates (not extending base.html) and include their own CSS/JS. They're perfect for login, registration, and password recovery flows.

### Login Pages

#### 1. Login (Version 1)
**Template:** `auth/login.html`

**Features:**
- Email/Username input
- Password with show/hide toggle
- Remember me checkbox
- Social login buttons (Facebook, Twitter, Google)
- Forgot password link
- Sign up link

**Screenshot:**
- Logo with profile image
- Primary colored header
- Professional layout

**Usage:**
```python
# urls.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
]
```

**View Example:**
```python
# views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'auth/login.html')
```

#### 2. Login 2 (Version 2)
**Template:** `auth/login2.html`

**Differences from Version 1:**
- Centered layout
- No profile image
- Email input instead of username
- Simplified header
- No social login buttons

**Usage:** Same as Login Version 1, just change template path.

---

### Register Pages

#### 1. Register (Version 1)
**Template:** `auth/register.html`

**Features:**
- Email input
- Username input
- Password input
- Password confirmation
- Form validation
- Social signup buttons
- Terms of service agreement
- Login link

**Usage:**
```python
# urls.py
path('register/', views.register_view, name='register'),
```

**View Example:**
```python
# views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validation
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'auth/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'auth/register.html')
```

#### 2. Register 2 (Version 2)
**Template:** `auth/register2.html`

**Differences:**
- Full name field instead of username
- Simplified layout
- Terms checkbox required
- No social signup buttons

---

### Password Reset Pages

#### 1. Recover Password (Version 1)
**Template:** `auth/password_reset.html`

**Features:**
- Email input for password reset
- Instructions message
- Link back to login

**Usage:**
```python
# urls.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),
]
```

**View Example:**
```python
# views.py
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            # Generate token and send email
            token = default_token_generator.make_token(user)

            # Send email (configure your email settings)
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: http://yourdomain.com/reset/{user.pk}/{token}/',
                'from@example.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Password reset link sent to your email')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Email not found')

    return render(request, 'auth/password_reset.html')
```

#### 2. Recover Password 2 (Version 2)
**Template:** `auth/password_reset2.html`

**Differences:**
- Simplified centered layout
- Right-aligned button

---

### Lock Screen Pages

#### 1. Lock Screen (Version 1)
**Template:** `auth/lock_screen.html`

**Features:**
- User avatar display
- Username display
- Password input to unlock
- Link to sign in as different user

**Usage:**
```python
# urls.py
path('lock-screen/', views.lock_screen, name='lock_screen'),
path('unlock/', views.unlock_screen, name='unlock_screen'),
```

**View Example:**
```python
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def lock_screen(request):
    # Store user session
    request.session['locked_user'] = request.user.username
    return render(request, 'auth/lock_screen.html')

def unlock_screen(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        username = request.session.get('locked_user')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            del request.session['locked_user']
            return redirect('home')
        else:
            messages.error(request, 'Invalid password')

    return render(request, 'auth/lock_screen.html')
```

#### 2. Lock Screen 2 (Version 2)
**Template:** `auth/lock_screen2.html`

**Differences:**
- Centered layout
- Right-aligned unlock button

---

### Email Confirmation Pages

#### 1. Email Confirmation (Version 1)
**Template:** `auth/email_confirmation.html`

**Features:**
- Mail icon
- Verification message
- Email display
- Verify button
- Resend link

**Usage:**
```python
# urls.py
path('confirm-email/', views.email_confirmation, name='email_confirmation'),
path('resend-verification/', views.resend_verification, name='resend_verification'),
```

**View Example:**
```python
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
import uuid

@login_required
def email_confirmation(request):
    user = request.user

    # Generate verification token
    token = str(uuid.uuid4())

    # Store token in session or database
    request.session['verification_token'] = token
    request.session['verification_email'] = user.email

    # Send verification email
    verification_link = f"http://yourdomain.com/verify-email/{token}/"
    send_mail(
        'Email Verification',
        f'Click to verify: {verification_link}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

    context = {'email': user.email}
    return render(request, 'auth/email_confirmation.html', context)

def resend_verification(request):
    # Resend verification email
    messages.success(request, 'Verification email resent')
    return redirect('email_confirmation')
```

#### 2. Email Confirmation 2 (Version 2)
**Template:** `auth/email_confirmation2.html`

**Features:**
- Success icon
- Success message
- Continue button

---

### Email Verification Pages

#### 1. Email Verification (Version 1)
**Template:** `auth/email_verification.html`

**Features:**
- Similar to confirmation but with card layout
- Profile image in header

#### 2. Email Verification 2 (Version 2)
**Template:** `auth/email_verification2.html`

**Features:**
- Success shield icon
- Verification complete message
- Continue button

**Usage:**
```python
# urls.py
path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
```

**View Example:**
```python
# views.py
def verify_email(request, token):
    stored_token = request.session.get('verification_token')

    if token == stored_token:
        # Mark email as verified
        request.user.email_verified = True  # Assuming you have this field
        request.user.save()

        del request.session['verification_token']

        messages.success(request, 'Email verified successfully!')
        return render(request, 'auth/email_verification2.html')
    else:
        messages.error(request, 'Invalid verification token')
        return redirect('email_confirmation')
```

---

### Two-Step Verification Pages

#### 1. Two-Step Verification (Version 1)
**Template:** `auth/two_step_verification.html`

**Features:**
- 4-digit code input
- Auto-focus next input
- Email display
- Resend code link

**Usage:**
```python
# urls.py
path('two-step-verify/', views.two_step_verify, name='two_step_verify'),
path('resend-code/', views.resend_code, name='resend_code'),
```

**View Example:**
```python
# views.py
import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def send_verification_code(email):
    """Generate and send 4-digit verification code"""
    code = str(random.randint(1000, 9999))

    send_mail(
        'Verification Code',
        f'Your verification code is: {code}',
        'from@example.com',
        [email],
        fail_silently=False,
    )

    return code

def two_step_verification(request):
    if request.method == 'POST':
        # User requested code
        email = request.user.email
        code = send_verification_code(email)

        # Store code in session
        request.session['verification_code'] = code
        request.session['verification_email'] = email

    context = {
        'email': request.session.get('verification_email', 'example@abc.com')
    }
    return render(request, 'auth/two_step_verification.html', context)

def two_step_verify(request):
    if request.method == 'POST':
        digit1 = request.POST.get('digit1', '')
        digit2 = request.POST.get('digit2', '')
        digit3 = request.POST.get('digit3', '')
        digit4 = request.POST.get('digit4', '')

        entered_code = digit1 + digit2 + digit3 + digit4
        stored_code = request.session.get('verification_code')

        if entered_code == stored_code:
            # Mark as verified
            request.session['two_step_verified'] = True
            del request.session['verification_code']

            messages.success(request, 'Verification successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid verification code')
            return redirect('two_step_verification')

    return redirect('two_step_verification')

def resend_code(request):
    email = request.session.get('verification_email')
    if email:
        code = send_verification_code(email)
        request.session['verification_code'] = code
        messages.success(request, 'Verification code resent')

    return redirect('two_step_verification')
```

**JavaScript for Auto-Focus (included in template):**
```javascript
// Auto-focus next input on digit entry
document.querySelectorAll('.two-step').forEach(function(input, index, inputs) {
    input.addEventListener('input', function() {
        if (this.value.length === 1 && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && this.value === '' && index > 0) {
            inputs[index - 1].focus();
        }
    });
});
```

#### 2. Two-Step Verification 2 (Version 2)
**Template:** `auth/two_step_verification2.html`

**Differences:**
- Lock icon instead of message icon
- Centered layout

---

## Utility Pages

### Starter Page

**Template:** `utility/starter.html`

**Extends:** `base/base.html`

**Features:**
- Page title with breadcrumbs
- Welcome message
- Getting started checklist
- Features list
- Call-to-action buttons

**Usage:**
```python
# urls.py
path('starter/', views.starter_page, name='starter_page'),
```

**View Example:**
```python
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def starter_page(request):
    return render(request, 'utility/starter.html')
```

**Customization:**
Edit the template to add your own content, checklists, or features.

---

### Maintenance Page

**Template:** `utility/maintenance.html`

**Features:**
- 503 styled error number
- Maintenance message
- Countdown timer
- Maintenance illustration

**Usage:**
```python
# urls.py
path('maintenance/', views.maintenance_page, name='maintenance'),

# Or in settings.py for site-wide maintenance
if MAINTENANCE_MODE:
    # Redirect all requests to maintenance page
```

**View Example:**
```python
# views.py
from django.shortcuts import render

def maintenance_page(request):
    return render(request, 'utility/maintenance.html')
```

**Middleware for Maintenance Mode:**
```python
# middleware.py
from django.shortcuts import render
from django.conf import settings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE:
            if not request.user.is_superuser:
                return render(request, 'utility/maintenance.html')

        return self.get_response(request)

# settings.py
MAINTENANCE_MODE = False  # Set to True to enable

MIDDLEWARE = [
    # ... other middleware
    'your_app.middleware.MaintenanceModeMiddleware',
]
```

**Countdown Customization:**
Change the countdown date in the template:
```html
<div data-countdown="2025/12/31" class="counter-number"></div>
```

---

### Coming Soon Page

**Template:** `utility/coming_soon.html`

**Features:**
- Logo display
- Coming soon message
- Countdown timer
- Email notification form
- Coming soon illustration

**Usage:**
```python
# urls.py
path('coming-soon/', views.coming_soon, name='coming_soon'),
path('notify-me/', views.notify_me, name='notify_me'),
```

**View Example:**
```python
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail

def coming_soon(request):
    return render(request, 'utility/coming_soon.html')

def notify_me(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Store email in database
        # NotificationSubscriber.objects.create(email=email)

        # Send confirmation email
        send_mail(
            'Launch Notification Subscription',
            'You will be notified when we launch!',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, 'Thank you! We will notify you when we launch.')
        return redirect('coming_soon')

    return redirect('coming_soon')
```

---

### Timeline Page

**Template:** `utility/timeline.html`

**Extends:** `base/base.html`

**Features:**
- Horizontal timeline with carousel
- Vertical timeline
- Event markers
- Responsive design

**Usage:**
```python
# urls.py
path('timeline/', views.timeline_page, name='timeline'),
```

**View Example:**
```python
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def timeline_page(request):
    # You can pass dynamic timeline data
    events = [
        {
            'date': '12 September',
            'title': 'First event',
            'description': 'Event description here...'
        },
        # ... more events
    ]

    context = {'events': events}
    return render(request, 'utility/timeline.html', context)
```

**Dynamic Timeline:**
Modify the template to use Django template variables:
```django
{% for event in events %}
<div class="item event-list">
    <div>
        <div class="event-date">
            <div class="text-primary mb-1">{{ event.date }}</div>
            <h5 class="mb-4">{{ event.title }}</h5>
        </div>
        <div class="mt-3 px-3">
            <p class="text-muted">{{ event.description }}</p>
        </div>
    </div>
</div>
{% endfor %}
```

---

### FAQs Page

**Template:** `utility/faqs.html`

**Extends:** `base/base.html`

**Features:**
- Vertical tab navigation
- Multiple FAQ categories
- Accordion for Q&A
- Icons for each category

**Usage:**
```python
# urls.py
path('faqs/', views.faqs_page, name='faqs'),
```

**View Example:**
```python
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def faqs_page(request):
    faqs = {
        'general': [
            {
                'question': 'What is Lorem Ipsum?',
                'answer': 'Lorem ipsum dolor sit amet...'
            },
            # ... more questions
        ],
        'privacy': [
            # ...
        ],
        'support': [
            # ...
        ]
    }

    context = {'faqs': faqs}
    return render(request, 'utility/faqs.html', context)
```

**Dynamic FAQs:**
```django
{% for category, questions in faqs.items %}
<div class="tab-pane" id="v-pills-{{ category }}">
    <h4 class="card-title mb-4">{{ category|title }}</h4>
    <div class="accordion" id="{{ category }}-accordion">
        {% for faq in questions %}
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#{{ category }}-{{ forloop.counter }}">
                    {{ faq.question }}
                </button>
            </h2>
            <div id="{{ category }}-{{ forloop.counter }}" class="accordion-collapse collapse">
                <div class="accordion-body">
                    {{ faq.answer }}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endfor %}
```

---

### Pricing Page

**Template:** `utility/pricing.html`

**Extends:** `base/base.html`

**Features:**
- 4 pricing tiers
- Feature comparison
- Call-to-action buttons
- Icons for each tier
- Responsive grid layout

**Usage:**
```python
# urls.py
path('pricing/', views.pricing_page, name='pricing'),
```

**View Example:**
```python
# views.py
from django.shortcuts import render

def pricing_page(request):
    plans = [
        {
            'name': 'Starter',
            'description': 'For small teams',
            'price': 19,
            'icon': 'bx bx-rocket',
            'features': [
                'Free Live Support',
                'Unlimited User',
                'No Time Tracking',
                'Free Setup'
            ]
        },
        {
            'name': 'Professional',
            'description': 'For medium teams',
            'price': 29,
            'icon': 'bx bx-trophy',
            'features': [
                'Free Live Support',
                'Unlimited User',
                'Time Tracking',
                'Free Setup'
            ]
        },
        # ... more plans
    ]

    context = {'plans': plans}
    return render(request, 'utility/pricing.html', context)
```

**Dynamic Pricing:**
```django
{% for plan in plans %}
<div class="col-xl-3 col-md-6">
    <div class="card plan-box">
        <div class="card-body p-4">
            <div class="d-flex">
                <div class="flex-grow-1">
                    <h5>{{ plan.name }}</h5>
                    <p class="text-muted">{{ plan.description }}</p>
                </div>
                <div class="flex-shrink-0">
                    <i class="{{ plan.icon }} h1 text-primary"></i>
                </div>
            </div>
            <div class="py-4">
                <h2><sup><small>$</small></sup> {{ plan.price }}/ <span class="font-size-13">Per month</span></h2>
            </div>
            <div class="text-center plan-btn">
                <a href="{% url 'subscribe' plan.name %}" class="btn btn-primary">Sign up Now</a>
            </div>
            <div class="plan-features mt-5">
                {% for feature in plan.features %}
                <p><i class="bx bx-checkbox-square text-primary me-2"></i> {{ feature }}</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endfor %}
```

---

### Error Pages

#### 404 Error Page

**Template:** `utility/error_404.html`

**Features:**
- 404 styled error
- Error message
- Back to dashboard button
- Error illustration

**Django Configuration:**
```python
# settings.py
DEBUG = False  # Error pages only work when DEBUG is False
ALLOWED_HOSTS = ['*']  # Configure properly for production

# urls.py (project root)
handler404 = 'your_app.views.custom_404'
```

**View Example:**
```python
# views.py
def custom_404(request, exception):
    return render(request, 'utility/error_404.html', status=404)
```

#### 500 Error Page

**Template:** `utility/error_500.html`

**Features:**
- 500 styled error
- Internal server error message
- Back to dashboard button

**Django Configuration:**
```python
# urls.py (project root)
handler500 = 'your_app.views.custom_500'
```

**View Example:**
```python
# views.py
def custom_500(request):
    return render(request, 'utility/error_500.html', status=500)
```

---

## URL Configuration

Complete URL configuration for all authentication and utility pages:

```python
# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.custom_login, name='login'),
    path('login2/', auth_views.LoginView.as_view(template_name='auth/login2.html'), name='login2'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register_view, name='register'),
    path('register2/', views.register_view_2, name='register2'),

    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset2/', views.password_reset_2, name='password_reset2'),

    path('lock-screen/', views.lock_screen, name='lock_screen'),
    path('lock-screen2/', views.lock_screen_2, name='lock_screen2'),
    path('unlock/', views.unlock_screen, name='unlock_screen'),

    path('confirm-email/', views.email_confirmation, name='email_confirmation'),
    path('confirm-email2/', views.email_confirmation_2, name='email_confirmation2'),

    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('email-verification/', views.email_verification, name='email_verification'),
    path('email-verification2/', views.email_verification_2, name='email_verification2'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    path('two-step/', views.two_step_verification, name='two_step_verification'),
    path('two-step2/', views.two_step_verification_2, name='two_step_verification2'),
    path('two-step-verify/', views.two_step_verify, name='two_step_verify'),
    path('resend-code/', views.resend_code, name='resend_code'),

    # Utility URLs
    path('starter/', views.starter_page, name='starter_page'),
    path('maintenance/', views.maintenance_page, name='maintenance'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('notify-me/', views.notify_me, name='notify_me'),
    path('timeline/', views.timeline_page, name='timeline'),
    path('faqs/', views.faqs_page, name='faqs'),
    path('pricing/', views.pricing_page, name='pricing'),
]

# Error handlers (in project root urls.py)
handler404 = 'your_app.views.custom_404'
handler500 = 'your_app.views.custom_500'
```

---

## Customization Guide

### Changing Colors

All pages use Bootstrap 5 color classes. To change colors:

**Method 1: Override Bootstrap Variables**
```scss
// custom.scss
$primary: #your-color;
$secondary: #your-color;

@import "bootstrap/scss/bootstrap";
```

**Method 2: Custom CSS**
```css
/* In your custom CSS file */
.bg-primary {
    background-color: #your-color !important;
}

.text-primary {
    color: #your-color !important;
}

.btn-primary {
    background-color: #your-color !important;
    border-color: #your-color !important;
}
```

### Changing Logo

Replace logo in all templates:
```django
<!-- Find and replace -->
<img src="{% static 'skote/images/logo.svg' %}" alt="">

<!-- With your logo -->
<img src="{% static 'your-app/images/your-logo.svg' %}" alt="Your Brand">
```

### Adding Custom Fields

Example: Add phone number to registration:

```python
# views.py
def register_view(request):
    if request.method == 'POST':
        # ... existing code
        phone = request.POST.get('phone')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Save phone in profile or extend User model
        profile = Profile.objects.create(user=user, phone=phone)

        # ... rest of code
```

```django
<!-- In auth/register.html -->
<div class="mb-3">
    <label for="phone" class="form-label">Phone Number</label>
    <input type="tel" class="form-control" id="phone" name="phone" required>
</div>
```

### Email Configuration

Configure Django email settings for password reset and verification:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Your App <noreply@yourapp.com>'

# For development, use console backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Social Authentication

To enable social login buttons:

1. Install `django-allauth`:
```bash
pip install django-allauth
```

2. Configure in settings:
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
]

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'your-client-id',
            'secret': 'your-secret',
        }
    }
}
```

3. Update templates:
```django
{% load socialaccount %}

<a href="{% provider_login_url 'google' %}" class="social-list-item bg-danger text-white border-danger">
    <i class="mdi mdi-google"></i>
</a>
```

### Custom Styling

Add custom CSS for specific pages:

```django
<!-- In any template -->
{% block extra_css %}
<style>
    .custom-auth-page {
        /* Your custom styles */
    }
</style>
{% endblock %}
```

Or create a dedicated CSS file:
```django
<!-- In template -->
<link href="{% static 'your-app/css/custom-auth.css' %}" rel="stylesheet">
```

---

## Best Practices

1. **Security:**
   - Always use CSRF tokens in forms
   - Use Django's built-in authentication system
   - Implement rate limiting for login attempts
   - Use HTTPS in production
   - Set secure session cookies

2. **User Experience:**
   - Provide clear error messages
   - Add loading indicators for async operations
   - Implement form validation (client and server-side)
   - Make forms accessible (ARIA labels, keyboard navigation)

3. **Email Verification:**
   - Send verification emails asynchronously (use Celery)
   - Set expiration time for verification tokens
   - Allow users to resend verification emails

4. **Password Security:**
   - Enforce strong password requirements
   - Use Django's password validators
   - Implement password strength meter
   - Never store plain text passwords

5. **Error Handling:**
   - Log all authentication errors
   - Provide user-friendly error messages
   - Don't reveal whether username/email exists (security)

---

## Testing Examples

```python
# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')

    def test_register_new_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_password_reset_sends_email(self):
        response = self.client.post(reverse('password_reset'), {
            'email': 'test@example.com'
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset', mail.outbox[0].subject)
```

---

## Troubleshooting

### Common Issues

**1. Templates not found**
```
Solution: Ensure skote_components is in INSTALLED_APPS
```

**2. Static files not loading**
```
Solution: Run python manage.py collectstatic
Check STATIC_URL and STATICFILES_DIRS settings
```

**3. Email not sending**
```
Solution: Check EMAIL_BACKEND settings
For development, use console backend
For production, configure SMTP properly
```

**4. Social login buttons not working**
```
Solution: Configure django-allauth properly
Add social app credentials in Django admin
```

**5. 404/500 pages not showing**
```
Solution: Set DEBUG = False
Configure ALLOWED_HOSTS
Define handler404 and handler500 in root urls.py
```

---

## Summary

You now have access to:

- **14 Authentication Pages**: Complete user authentication flows
- **8 Utility Pages**: Essential application pages
- **Full Customization**: Easily modify colors, logos, and content
- **Production Ready**: Security best practices included
- **Well Documented**: Complete examples and usage guides

All templates are responsive, accessible, and follow Django best practices. Start with the basic templates and customize as needed for your project!

For more information, see:
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- [COMPONENTS.md](COMPONENTS.md) - Component reference
- [TABLES_AND_FORMS.md](TABLES_AND_FORMS.md) - Tables and forms guide

**Happy coding!** 🚀
