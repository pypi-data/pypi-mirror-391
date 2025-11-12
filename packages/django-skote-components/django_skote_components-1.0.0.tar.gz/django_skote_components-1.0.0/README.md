# Skote Components - Django Component Library

A comprehensive Django component library based on the **Skote Bootstrap 5 Admin Template**. This library provides reusable UI components, form fields, and layout templates for building modern admin dashboards and web applications.

## Features

- **Complete Layout System** - Base templates with header, sidebar, footer, and theme customization
- **UI Components** - Alerts, cards, badges, buttons, modals, breadcrumbs, progress bars, and icons
- **Form Components** - Styled form fields with Django form integration
- **Bootstrap 5** - Built on Bootstrap 5 with full responsive design
- **Multiple Themes** - Light, Dark, RTL, and Dark RTL modes
- **Icon Libraries** - Boxicons, Material Design, Font Awesome, and Dripicons included
- **Chart Libraries** - ApexCharts, ECharts, Chart.js integration ready
- **Easy Integration** - Simple template tags and inclusion templates

## Installation

### 1. Copy the Component Library

Copy the `skote_components` directory into your Django project.

### 2. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'skote_components',
]
```

### 3. Configure Static Files

```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'skote_components' / 'static',
]
```

### 4. Run Collectstatic (for production)

```bash
python manage.py collectstatic
```

## Quick Start

### Basic Template Setup

```django
{% extends 'base/base.html' %}
{% load skote_components %}

{% block title %}My Page{% endblock %}

{% block page_heading %}Dashboard{% endblock %}

{% block breadcrumb_active %}Dashboard{% endblock %}

{% block content %}
    <div class="row">
        <div class="col-md-6">
            {% skote_alert "Welcome to your dashboard!" type="success" icon="bx bx-check-circle" %}
        </div>
    </div>
{% endblock %}
```

### Customize Sidebar

Create a custom template that extends the base and overrides the sidebar:

```django
{% extends 'base/base.html' %}

{% block sidebar_menu %}
<li class="menu-title">Menu</li>

<li>
    <a href="{% url 'dashboard' %}" class="waves-effect">
        <i class="bx bx-home-circle"></i>
        <span>Dashboard</span>
    </a>
</li>

<li>
    <a href="javascript: void(0);" class="has-arrow waves-effect">
        <i class="bx bx-store"></i>
        <span>Products</span>
    </a>
    <ul class="sub-menu" aria-expanded="false">
        <li><a href="{% url 'product_list' %}">All Products</a></li>
        <li><a href="{% url 'product_create' %}">Add Product</a></li>
    </ul>
</li>
{% endblock %}
```

## UI Components

### Alerts

```django
{% load skote_components %}

{# Basic alert #}
{% skote_alert "This is a success message!" type="success" %}

{# Alert with icon #}
{% skote_alert "Warning message" type="warning" icon="bx bx-error" %}

{# Non-dismissible alert #}
{% skote_alert "Info message" type="info" dismissible=False %}
```

**Parameters:**
- `message` - Alert text (required)
- `type` - Alert color: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark` (default: `primary`)
- `dismissible` - Show close button (default: `True`)
- `icon` - Icon class (optional)

### Cards

```django
{% load skote_components %}

{# Simple card #}
{% skote_card title="Card Title" content="Card content goes here" %}

{# Card with subtitle #}
{% skote_card title="Statistics" subtitle="Monthly overview" content="<p>Your content</p>" %}

{# Card with footer #}
{% skote_card title="Actions" content="Main content" footer="<button class='btn btn-primary'>Save</button>" %}
```

**Parameters:**
- `title` - Card title (optional)
- `subtitle` - Card subtitle (optional)
- `content` - HTML content for card body (optional)
- `footer` - HTML content for card footer (optional)
- `card_class` - Additional CSS classes for card (optional)
- `header_class` - Additional CSS classes for header (optional)
- `body_class` - Additional CSS classes for body (optional)
- `footer_class` - Additional CSS classes for footer (optional)

### Badges

```django
{% load skote_components %}

{# Standard badge #}
{% skote_badge "New" type="primary" %}

{# Rounded pill badge #}
{% skote_badge "5" type="danger" rounded=True %}

{# Soft badge #}
{% skote_badge "Info" type="info" soft=True %}
```

**Parameters:**
- `text` - Badge text (required)
- `type` - Badge color (default: `primary`)
- `rounded` - Use pill style (default: `False`)
- `soft` - Use soft/subtle background (default: `False`)

### Buttons

```django
{% load skote_components %}

{# Basic button #}
{% skote_button "Submit" type="primary" %}

{# Button with icon #}
{% skote_button "Save" type="success" icon="bx bx-check" %}

{# Outline button #}
{% skote_button "Cancel" type="secondary" outline=True %}

{# Large button #}
{% skote_button "Continue" type="primary" size="lg" %}

{# Button as link #}
{% skote_button "View Details" type="info" href="/details/" %}
```

**Parameters:**
- `text` - Button text (required)
- `type` - Button color (default: `primary`)
- `size` - Button size: `sm`, `lg`, or empty (optional)
- `outline` - Use outline style (default: `False`)
- `block` - Full width button (default: `False`)
- `disabled` - Disabled state (default: `False`)
- `href` - Render as link (optional)
- `icon` - Icon class (optional)
- `icon_position` - Icon position: `left` or `right` (default: `left`)

### Modals

```django
{% load skote_components %}

{# Basic modal #}
{% skote_modal "confirmModal" "Confirm Action" body="<p>Are you sure?</p>" %}

{# Large centered modal with buttons #}
{% skote_modal "detailsModal" "Details" size="lg" centered=True footer_buttons=buttons %}

<!-- Button to trigger modal -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#confirmModal">
    Open Modal
</button>
```

**In your view, define footer_buttons:**

```python
buttons = [
    {'text': 'Close', 'type': 'secondary', 'dismiss': True},
    {'text': 'Save Changes', 'type': 'primary'},
]
context['buttons'] = buttons
```

**Parameters:**
- `modal_id` - Unique modal ID (required)
- `title` - Modal title (required)
- `body` - HTML content for modal body (optional)
- `size` - Modal size: `sm`, `lg`, `xl`, or empty (optional)
- `centered` - Vertically center (default: `False`)
- `scrollable` - Enable scrolling (default: `False`)
- `footer_buttons` - List of button configs (optional)

### Breadcrumbs

```django
{% load skote_components %}

{% skote_breadcrumb breadcrumb_items %}
```

**In your view:**

```python
breadcrumb_items = [
    {'text': 'Home', 'url': '/'},
    {'text': 'Products', 'url': '/products/'},
    {'text': 'Detail'}  # Last item is active (no URL)
]
context['breadcrumb_items'] = breadcrumb_items
```

### Progress Bars

```django
{% load skote_components %}

{# Basic progress bar #}
{% skote_progress 75 type="success" %}

{# Striped animated progress bar #}
{% skote_progress 60 type="primary" striped=True animated=True %}

{# With custom label #}
{% skote_progress 45 type="warning" label="45% Complete" %}

{# Custom height #}
{% skote_progress 80 type="info" height="20px" %}
```

**Parameters:**
- `value` - Current value (required)
- `max_value` - Maximum value (default: `100`)
- `type` - Color type (default: `primary`)
- `striped` - Show stripes (default: `False`)
- `animated` - Animate stripes (default: `False`)
- `label` - Custom label (optional, defaults to percentage)
- `height` - Custom height (optional)

### Icons

```django
{% load skote_components %}

{# Basic icon #}
{% skote_icon 'bx bx-home' %}

{# Icon with custom size and color #}
{% skote_icon 'mdi mdi-account' size='24px' color='primary' %}

{# Icon with hex color #}
{% skote_icon 'bx bx-check-circle' size='2rem' color='#28a745' %}
```

## Form Components

### Text Input

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_input field=form.email %}

{# Manual input #}
{% skote_input label="Email Address" name="email" input_type="email" required=True placeholder="Enter email" %}
```

### Select Dropdown

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_select field=form.country %}

{# Manual select #}
{% skote_select label="Country" name="country" choices=countries required=True %}
```

**In your view:**

```python
countries = [
    ('us', 'United States'),
    ('uk', 'United Kingdom'),
    ('ca', 'Canada'),
]
context['countries'] = countries
```

### Textarea

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_textarea field=form.description %}

{# Manual textarea #}
{% skote_textarea label="Description" name="description" rows=5 placeholder="Enter description" %}
```

### Checkbox / Switch

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_checkbox field=form.agree %}

{# Manual checkbox #}
{% skote_checkbox label="Remember me" name="remember" %}

{# Switch style #}
{% skote_checkbox label="Enable notifications" name="notifications" switch=True %}
```

### Radio Buttons

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_radio field=form.gender %}

{# Manual radio buttons #}
{% skote_radio label="Size" name="size" choices=sizes inline=True %}
```

**In your view:**

```python
sizes = [
    ('s', 'Small'),
    ('m', 'Medium'),
    ('l', 'Large'),
]
context['sizes'] = sizes
```

### File Upload

```django
{% load skote_forms %}

{# With Django form field #}
{% skote_file_upload field=form.document %}

{# Manual file upload #}
{% skote_file_upload label="Upload Image" name="image" accept="image/*" %}

{# Multiple files #}
{% skote_file_upload label="Upload Documents" name="docs" accept=".pdf,.doc,.docx" multiple=True %}
```

## Complete Form Example

```django
{% extends 'base/base.html' %}
{% load skote_forms skote_components %}

{% block content %}
<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Product Form</h4>

                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}

                    {% skote_input field=form.name %}
                    {% skote_textarea field=form.description %}
                    {% skote_select field=form.category %}
                    {% skote_input field=form.price %}
                    {% skote_checkbox field=form.is_active switch=True %}
                    {% skote_file_upload field=form.image %}

                    <div class="mt-3">
                        {% skote_button "Save Product" type="primary" icon="bx bx-check" %}
                        {% skote_button "Cancel" type="secondary" outline=True href="{% url 'product_list' %}" %}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Layout Customization

### Custom Header

Override header template variables in your view:

```python
def my_view(request):
    context = {
        'notifications_count': 5,
        'recent_notifications': Notification.objects.filter(user=request.user)[:5],
    }
    return render(request, 'my_template.html', context)
```

### Custom Footer

Create `templates/layouts/custom_footer.html`:

```django
{% extends 'base/base.html' %}

{% block footer_company %}My Company{% endblock %}

{% block footer_credits %}
Powered by <a href="https://example.com">My Team</a>
{% endblock %}
```

### Theme Customization

Users can customize theme via the right sidebar settings panel (click gear icon in header).

Themes persist in browser sessionStorage automatically.

## URL Configuration

Your project needs these URL names for header links to work:

```python
# urls.py
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

## Chart Integration

The template includes several chart libraries. Example with ApexCharts:

```django
{% extends 'base/base.html' %}

{% block extra_js %}
<script src="{% static 'skote/libs/apexcharts/apexcharts.min.js' %}"></script>
{% endblock %}

{% block inline_js %}
<script>
var options = {
    series: [{
        name: 'Sales',
        data: [30, 40, 35, 50, 49, 60, 70]
    }],
    chart: {
        type: 'area',
        height: 350
    },
    xaxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
    }
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();
</script>
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Sales Chart</h4>
                <div id="chart"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Advanced Examples

### Dashboard with Multiple Components

```django
{% extends 'base/base.html' %}
{% load skote_components %}

{% block content %}
<div class="row">
    <!-- Stats Cards -->
    <div class="col-md-3">
        <div class="card mini-stats-wid">
            <div class="card-body">
                <div class="d-flex">
                    <div class="flex-grow-1">
                        <p class="text-muted fw-medium">Total Sales</p>
                        <h4 class="mb-0">$35,420</h4>
                    </div>
                    <div class="avatar-sm rounded-circle bg-primary align-self-center">
                        <span class="avatar-title rounded-circle bg-primary">
                            {% skote_icon 'bx bx-shopping-bag' size='24px' color='white' %}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add more stat cards -->
</div>

<div class="row">
    <div class="col-lg-8">
        {% skote_card title="Recent Orders" content=order_table %}
    </div>

    <div class="col-lg-4">
        {% skote_card title="Activity" content=activity_feed %}
    </div>
</div>
{% endblock %}
```

## Available Icon Libraries

- **Boxicons** - `bx bx-home`, `bx bx-user`, etc.
- **Material Design Icons** - `mdi mdi-account`, `mdi mdi-home`, etc.
- **Font Awesome** - `fas fa-user`, `far fa-envelope`, etc.
- **Dripicons** - Use classes from Dripicons documentation

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- No IE11 support (Bootstrap 5 requirement)

## License

This component library is based on the Skote Admin Template by Themesbrand.

## Support

For issues or questions:
1. Check this documentation
2. Review the original Skote template files in `skote/layouts/`
3. Consult Bootstrap 5 documentation for component customization

## Contributing

To add new components:
1. Create template tag in `templatetags/skote_components.py` or `skote_forms.py`
2. Create inclusion template in `templates/components/ui/` or `templates/components/forms/`
3. Update this README with usage examples
4. Test with sample data
