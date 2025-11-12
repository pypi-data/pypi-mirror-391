# Skote Components - Quick Start Guide

Get up and running with Skote Components in 5 minutes.

## Step 1: Installation

1. Copy `skote_components` folder to your Django project root
2. Add to `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
    'skote_components',  # Add this
]
```

3. Configure static files:

```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'skote_components' / 'static',
]
```

## Step 2: Configure URLs

Make sure your project has these named URLs (header navigation depends on them):

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
]
```

## Step 3: Create Your First Page

```python
# views.py
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
```

```django
<!-- templates/home.html -->
{% extends 'base/base.html' %}
{% load skote_components %}

{% block title %}Home{% endblock %}
{% block page_heading %}Dashboard{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        {% skote_alert "Welcome to your dashboard!" type="success" icon="bx bx-check-circle" %}

        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Getting Started</h4>
                <p>Your Skote component library is ready to use!</p>
                {% skote_button "Explore Components" type="primary" href="/components/" %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Step 4: Customize the Sidebar

Create `templates/my_base.html`:

```django
{% extends 'base/base.html' %}

{% block sidebar_menu %}
<li class="menu-title">Main Menu</li>

<li>
    <a href="{% url 'home' %}" class="waves-effect">
        <i class="bx bx-home-circle"></i>
        <span>Dashboard</span>
    </a>
</li>

<li>
    <a href="javascript: void(0);" class="has-arrow waves-effect">
        <i class="bx bx-user"></i>
        <span>Users</span>
    </a>
    <ul class="sub-menu" aria-expanded="false">
        <li><a href="{% url 'user_list' %}">All Users</a></li>
        <li><a href="{% url 'user_create' %}">Add User</a></li>
    </ul>
</li>

<li>
    <a href="{% url 'settings' %}" class="waves-effect">
        <i class="bx bx-cog"></i>
        <span>Settings</span>
    </a>
</li>
{% endblock %}
```

Then extend from `my_base.html` in your pages:

```django
{% extends 'my_base.html' %}
{% block content %}
    <!-- Your content -->
{% endblock %}
```

## Step 5: Create a Form

```python
# forms.py
from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    category = forms.ChoiceField(choices=[
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
    ])
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    is_active = forms.BooleanField(required=False)
    image = forms.ImageField(required=False)
```

```django
<!-- templates/product_form.html -->
{% extends 'my_base.html' %}
{% load skote_forms skote_components %}

{% block content %}
<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Add Product</h4>

                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}

                    {% skote_input field=form.name %}
                    {% skote_textarea field=form.description %}
                    {% skote_select field=form.category %}
                    {% skote_input field=form.price %}
                    {% skote_checkbox field=form.is_active switch=True %}
                    {% skote_file_upload field=form.image %}

                    <div class="mt-3">
                        {% skote_button "Save Product" type="primary" icon="bx bx-save" %}
                        {% skote_button "Cancel" type="secondary" outline=True href="{% url 'home' %}" %}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ProductForm

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save your product
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form})
```

## Common UI Components Cheat Sheet

```django
{% load skote_components %}

{# Alerts #}
{% skote_alert "Success message" type="success" %}
{% skote_alert "Error message" type="danger" icon="bx bx-error" %}

{# Buttons #}
{% skote_button "Click Me" type="primary" %}
{% skote_button "Delete" type="danger" outline=True icon="bx bx-trash" %}

{# Badges #}
{% skote_badge "New" type="primary" rounded=True %}
{% skote_badge "Active" type="success" soft=True %}

{# Cards #}
{% skote_card title="My Card" content="<p>Card content</p>" %}

{# Progress Bar #}
{% skote_progress 75 type="success" striped=True %}

{# Icons #}
{% skote_icon 'bx bx-home' size='24px' color='primary' %}
```

## Form Components Cheat Sheet

```django
{% load skote_forms %}

{# Text Input #}
{% skote_input field=form.email %}
{% skote_input label="Name" name="name" required=True %}

{# Textarea #}
{% skote_textarea field=form.description %}

{# Select Dropdown #}
{% skote_select field=form.category %}

{# Checkbox #}
{% skote_checkbox label="Remember me" name="remember" %}
{% skote_checkbox label="Notifications" name="notify" switch=True %}

{# File Upload #}
{% skote_file_upload field=form.document %}
```

## Running the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see your application with Skote components!

## Next Steps

- Read the full [README.md](README.md) for all component options
- Check [EXAMPLES.md](EXAMPLES.md) for real-world usage examples
- Customize templates in `skote_components/templates/`
- Add your own template tags in `templatetags/`

## Troubleshooting

### Static files not loading

Run:
```bash
python manage.py collectstatic
```

Or in development, make sure you have:
```python
# settings.py
DEBUG = True
```

### Template not found error

Make sure `skote_components` is in `INSTALLED_APPS`.

### URL not found error

Check that all required URLs are named in `urls.py`:
- `home`
- `search`
- `notifications`
- `profile`
- `settings`
- `login`
- `logout`

You can create placeholder views for URLs you don't need yet.

## Support

For more information, see:
- Full documentation: [README.md](README.md)
- Code examples: [EXAMPLES.md](EXAMPLES.md)
- Original Skote template: `skote/layouts/`

Happy coding! 🚀
