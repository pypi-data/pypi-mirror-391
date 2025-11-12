# Skote Components - Usage Examples

This file contains practical examples of using Skote components in real-world scenarios.

## Example 1: User Dashboard

```django
{% extends 'base/base.html' %}
{% load skote_components %}

{% block title %}Dashboard{% endblock %}
{% block page_heading %}Dashboard{% endblock %}

{% block content %}
<!-- Stats Row -->
<div class="row">
    <div class="col-xl-3 col-md-6">
        <div class="card">
            <div class="card-body">
                <div class="d-flex">
                    <div class="flex-grow-1">
                        <p class="text-muted fw-medium mb-2">Total Users</p>
                        <h4 class="mb-0">{{ total_users }}</h4>
                    </div>
                    <div class="flex-shrink-0 align-self-center">
                        <div class="avatar-sm rounded-circle bg-primary mini-stat-icon">
                            <span class="avatar-title rounded-circle bg-primary">
                                {% skote_icon 'bx bx-user' size='24px' color='white' %}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6">
        <div class="card">
            <div class="card-body">
                <div class="d-flex">
                    <div class="flex-grow-1">
                        <p class="text-muted fw-medium mb-2">Revenue</p>
                        <h4 class="mb-0">${{ revenue }}</h4>
                    </div>
                    <div class="flex-shrink-0 align-self-center">
                        <div class="avatar-sm rounded-circle bg-success mini-stat-icon">
                            <span class="avatar-title rounded-circle bg-success">
                                {% skote_icon 'bx bx-dollar' size='24px' color='white' %}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Activity -->
<div class="row">
    <div class="col-lg-12">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Recent Activity</h4>

                {% for activity in recent_activities %}
                <div class="d-flex align-items-center mb-3">
                    <div class="avatar-xs me-3">
                        <span class="avatar-title rounded-circle bg-primary-subtle text-primary">
                            {% skote_icon activity.icon %}
                        </span>
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-0">{{ activity.title }}</h6>
                        <p class="text-muted mb-0">{{ activity.description }}</p>
                    </div>
                    <div class="flex-shrink-0">
                        <span class="text-muted">{{ activity.created_at|timesince }} ago</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Example 2: Product Management Page

```django
{% extends 'base/base.html' %}
{% load skote_components %}

{% block title %}Products{% endblock %}
{% block page_heading %}Product Management{% endblock %}

{% block breadcrumb %}
<div class="page-title-right">
    {% skote_breadcrumb breadcrumb_items %}
</div>
{% endblock %}

{% block content %}
<!-- Success message -->
{% if messages %}
    {% for message in messages %}
        {% if message.tags == 'success' %}
            {% skote_alert message type="success" icon="bx bx-check-circle" %}
        {% elif message.tags == 'error' %}
            {% skote_alert message type="danger" icon="bx bx-error-circle" %}
        {% endif %}
    {% endfor %}
{% endif %}

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="card-title mb-0">All Products</h4>
                    {% skote_button "Add Product" type="primary" icon="bx bx-plus" href="{% url 'product_create' %}" %}
                </div>

                <div class="table-responsive">
                    <table class="table table-centered table-nowrap mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Product</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for product in products %}
                            <tr>
                                <td>
                                    <h6 class="mb-0">{{ product.name }}</h6>
                                    <p class="text-muted mb-0">{{ product.sku }}</p>
                                </td>
                                <td>{{ product.category }}</td>
                                <td>${{ product.price }}</td>
                                <td>{{ product.stock }}</td>
                                <td>
                                    {% if product.is_active %}
                                        {% skote_badge "Active" type="success" soft=True %}
                                    {% else %}
                                        {% skote_badge "Inactive" type="danger" soft=True %}
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'product_edit' product.id %}" class="btn btn-sm btn-primary">
                                        {% skote_icon 'bx bx-edit' %}
                                    </a>
                                    <button class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#deleteModal{{ product.id }}">
                                        {% skote_icon 'bx bx-trash' %}
                                    </button>
                                </td>
                            </tr>

                            <!-- Delete Confirmation Modal -->
                            {% skote_modal modal_id=delete_modal_id title="Confirm Delete" size="sm" centered=True footer_buttons=delete_buttons %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**View code:**

```python
def product_list(request):
    products = Product.objects.all()

    breadcrumb_items = [
        {'text': 'Home', 'url': reverse('home')},
        {'text': 'Products'}
    ]

    delete_buttons = [
        {'text': 'Cancel', 'type': 'secondary', 'dismiss': True},
        {'text': 'Delete', 'type': 'danger'},
    ]

    context = {
        'products': products,
        'breadcrumb_items': breadcrumb_items,
        'delete_buttons': delete_buttons,
    }
    return render(request, 'products/list.html', context)
```

## Example 3: User Profile Form

```django
{% extends 'base/base.html' %}
{% load skote_forms skote_components %}

{% block title %}Edit Profile{% endblock %}
{% block page_heading %}Profile Settings{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Personal Information</h4>

                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}

                    <div class="row">
                        <div class="col-md-6">
                            {% skote_input field=form.first_name %}
                        </div>
                        <div class="col-md-6">
                            {% skote_input field=form.last_name %}
                        </div>
                    </div>

                    {% skote_input field=form.email %}
                    {% skote_input field=form.phone %}
                    {% skote_textarea field=form.bio %}

                    <h5 class="font-size-14 mb-3">Preferences</h5>

                    {% skote_select field=form.timezone %}
                    {% skote_select field=form.language %}

                    <h5 class="font-size-14 mb-3">Notifications</h5>

                    {% skote_checkbox field=form.email_notifications switch=True %}
                    {% skote_checkbox field=form.sms_notifications switch=True %}

                    <h5 class="font-size-14 mb-3">Profile Picture</h5>

                    {% skote_file_upload field=form.avatar %}

                    <div class="mt-4">
                        {% skote_button "Save Changes" type="primary" icon="bx bx-save" %}
                        {% skote_button "Cancel" type="secondary" outline=True href="{% url 'profile' %}" %}
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Profile Completion</h4>

                <div class="mb-3">
                    <span class="text-muted">Your profile is {{ profile_completion }}% complete</span>
                    {% skote_progress profile_completion type="success" striped=True animated=True %}
                </div>

                <div class="mt-4">
                    {% skote_alert "Complete your profile to unlock all features!" type="info" icon="bx bx-info-circle" dismissible=False %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Example 4: Data Table with Actions

```django
{% extends 'base/base.html' %}
{% load skote_components %}

{% block extra_css %}
<link href="{% static 'skote/libs/datatables.net-bs4/css/dataTables.bootstrap4.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Orders</h4>
                <p class="card-title-desc">View and manage customer orders</p>

                <table id="ordersTable" class="table table-bordered dt-responsive nowrap w-100">
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Customer</th>
                            <th>Date</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders %}
                        <tr>
                            <td>#{{ order.id }}</td>
                            <td>{{ order.customer.name }}</td>
                            <td>{{ order.created_at|date:"M d, Y" }}</td>
                            <td>${{ order.total }}</td>
                            <td>
                                {% if order.status == 'completed' %}
                                    {% skote_badge "Completed" type="success" %}
                                {% elif order.status == 'pending' %}
                                    {% skote_badge "Pending" type="warning" %}
                                {% elif order.status == 'cancelled' %}
                                    {% skote_badge "Cancelled" type="danger" %}
                                {% else %}
                                    {% skote_badge order.status|title type="info" %}
                                {% endif %}
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <a href="{% url 'order_detail' order.id %}" class="btn btn-sm btn-outline-primary">
                                        View
                                    </a>
                                    <a href="{% url 'order_invoice' order.id %}" class="btn btn-sm btn-outline-secondary">
                                        Invoice
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/datatables.net/js/jquery.dataTables.min.js' %}"></script>
<script src="{% static 'skote/libs/datatables.net-bs4/js/dataTables.bootstrap4.min.js' %}"></script>
{% endblock %}

{% block inline_js %}
<script>
$(document).ready(function() {
    $('#ordersTable').DataTable({
        order: [[2, 'desc']],
        pageLength: 25,
    });
});
</script>
{% endblock %}
```

## Example 5: Settings Page with Tabs

```django
{% extends 'base/base.html' %}
{% load skote_forms skote_components %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Application Settings</h4>

                <ul class="nav nav-tabs nav-tabs-custom" role="tablist">
                    <li class="nav-item">
                        <a class="nav-link active" data-bs-toggle="tab" href="#general" role="tab">
                            {% skote_icon 'bx bx-cog' %} General
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" data-bs-toggle="tab" href="#email" role="tab">
                            {% skote_icon 'bx bx-envelope' %} Email
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" data-bs-toggle="tab" href="#security" role="tab">
                            {% skote_icon 'bx bx-lock' %} Security
                        </a>
                    </li>
                </ul>

                <div class="tab-content p-3">
                    <div class="tab-pane active" id="general" role="tabpanel">
                        <form method="post">
                            {% csrf_token %}
                            {% skote_input label="Site Name" name="site_name" value=settings.site_name required=True %}
                            {% skote_input label="Support Email" name="support_email" input_type="email" value=settings.support_email %}
                            {% skote_select label="Timezone" name="timezone" choices=timezones selected=settings.timezone %}
                            {% skote_checkbox label="Maintenance Mode" name="maintenance_mode" checked=settings.maintenance_mode switch=True %}

                            {% skote_button "Save Settings" type="primary" icon="bx bx-save" %}
                        </form>
                    </div>

                    <div class="tab-pane" id="email" role="tabpanel">
                        <form method="post">
                            {% csrf_token %}
                            {% skote_input label="SMTP Host" name="smtp_host" value=settings.smtp_host %}
                            {% skote_input label="SMTP Port" name="smtp_port" input_type="number" value=settings.smtp_port %}
                            {% skote_input label="SMTP Username" name="smtp_username" value=settings.smtp_username %}
                            {% skote_input label="SMTP Password" name="smtp_password" input_type="password" %}

                            {% skote_button "Save Settings" type="primary" icon="bx bx-save" %}
                            {% skote_button "Test Connection" type="info" outline=True icon="bx bx-paper-plane" %}
                        </form>
                    </div>

                    <div class="tab-pane" id="security" role="tabpanel">
                        {% skote_alert "These settings affect application security. Change with caution." type="warning" icon="bx bx-error" %}

                        <form method="post">
                            {% csrf_token %}
                            {% skote_checkbox label="Two-Factor Authentication" name="2fa_enabled" checked=settings.two_factor_enabled switch=True %}
                            {% skote_checkbox label="Force HTTPS" name="force_https" checked=settings.force_https switch=True %}
                            {% skote_input label="Session Timeout (minutes)" name="session_timeout" input_type="number" value=settings.session_timeout %}

                            {% skote_button "Save Settings" type="primary" icon="bx bx-save" %}
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Example 6: Login Page (No Layout)

Create `templates/auth/login.html`:

```django
{% load static skote_forms skote_components %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Login | Your App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link href="{% static 'skote/css/bootstrap.min.css' %}" rel="stylesheet">
    <link href="{% static 'skote/css/icons.min.css' %}" rel="stylesheet">
    <link href="{% static 'skote/css/app.min.css' %}" rel="stylesheet">
</head>

<body>
    <div class="account-pages my-5 pt-sm-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8 col-lg-6 col-xl-5">
                    <div class="card overflow-hidden">
                        <div class="bg-primary bg-soft">
                            <div class="row">
                                <div class="col-7">
                                    <div class="text-primary p-4">
                                        <h5 class="text-primary">Welcome Back!</h5>
                                        <p>Sign in to continue</p>
                                    </div>
                                </div>
                                <div class="col-5 align-self-end">
                                    <img src="{% static 'skote/images/profile-img.png' %}" alt="" class="img-fluid">
                                </div>
                            </div>
                        </div>
                        <div class="card-body pt-0">
                            <div class="p-2">
                                {% if messages %}
                                    {% for message in messages %}
                                        {% skote_alert message type=message.tags %}
                                    {% endfor %}
                                {% endif %}

                                <form method="post" class="form-horizontal">
                                    {% csrf_token %}

                                    {% skote_input field=form.username %}
                                    {% skote_input field=form.password %}
                                    {% skote_checkbox label="Remember me" name="remember" %}

                                    <div class="mt-3 d-grid">
                                        {% skote_button "Log In" type="primary" block=True %}
                                    </div>

                                    <div class="mt-4 text-center">
                                        <a href="{% url 'password_reset' %}" class="text-muted">
                                            {% skote_icon 'bx bx-lock-open' %} Forgot password?
                                        </a>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div class="mt-5 text-center">
                        <p>Don't have an account? <a href="{% url 'register' %}" class="fw-medium text-primary">Signup now</a></p>
                        <p>© {{ current_year }} Your Company</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="{% static 'skote/libs/jquery/jquery.min.js' %}"></script>
    <script src="{% static 'skote/libs/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
</body>
</html>
```

## Tips and Best Practices

### 1. Consistent Component Usage

Always use template tags for consistency:

```django
{# Good #}
{% skote_button "Submit" type="primary" %}

{# Avoid #}
<button class="btn btn-primary">Submit</button>
```

### 2. Reusable Partials

Create reusable components for common patterns:

```django
{# templates/partials/stat_card.html #}
<div class="col-xl-3 col-md-6">
    <div class="card">
        <div class="card-body">
            <div class="d-flex">
                <div class="flex-grow-1">
                    <p class="text-muted fw-medium mb-2">{{ label }}</p>
                    <h4 class="mb-0">{{ value }}</h4>
                </div>
                <div class="flex-shrink-0 align-self-center">
                    <div class="avatar-sm rounded-circle bg-{{ color }} mini-stat-icon">
                        <span class="avatar-title rounded-circle bg-{{ color }}">
                            {% skote_icon icon size='24px' color='white' %}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{# Usage #}
{% include 'partials/stat_card.html' with label="Users" value=total_users color="primary" icon="bx bx-user" %}
```

### 3. Context Processors

Create a context processor for common data:

```python
# context_processors.py
def site_settings(request):
    return {
        'site_name': 'My App',
        'current_year': datetime.now().year,
    }
```

### 4. Custom Template Tags

Extend with your own tags:

```python
# templatetags/custom_tags.py
from django import template
from skote_components.templatetags.skote_components import register

@register.simple_tag
def status_badge(status):
    status_map = {
        'active': ('Active', 'success'),
        'pending': ('Pending', 'warning'),
        'inactive': ('Inactive', 'danger'),
    }
    text, badge_type = status_map.get(status, (status.title(), 'secondary'))
    return mark_safe(f'<span class="badge bg-{badge_type}">{text}</span>')
```

These examples demonstrate real-world usage patterns for the Skote component library.
