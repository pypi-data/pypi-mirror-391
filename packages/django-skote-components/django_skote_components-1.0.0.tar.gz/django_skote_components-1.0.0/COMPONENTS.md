# Complete Component Reference

This document provides a comprehensive reference for all 30+ Skote components.

## UI Components

### 1. Alerts
Display contextual feedback messages.

```django
{% load skote_components %}

{# Basic alerts #}
{% skote_alert "Success message!" type="success" %}
{% skote_alert "Warning!" type="warning" dismissible=False %}
{% skote_alert "Error occurred" type="danger" icon="bx bx-error-circle" %}
```

**Types:** `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`

---

### 2. Badges
Small count and labeling component.

```django
{% skote_badge "New" type="primary" %}
{% skote_badge "5" type="danger" rounded=True %}
{% skote_badge "Active" type="success" soft=True %}
```

---

### 3. Buttons
Trigger actions and events.

```django
{% skote_button "Submit" type="primary" %}
{% skote_button "Delete" type="danger" outline=True icon="bx bx-trash" %}
{% skote_button "Large Button" size="lg" block=True %}
{% skote_button "Link Button" href="/page/" type="info" %}
```

---

### 4. Cards
Flexible content containers.

```django
{% skote_card title="Card Title" subtitle="Subtitle" content="<p>Card content</p>" %}
{% skote_card title="With Footer" content="Main content" footer="<button class='btn btn-primary'>Action</button>" %}
```

---

### 5. Carousel
Slideshow component for cycling through images.

```django
{% skote_carousel "myCarousel" slides controls=True indicators=True %}

{# In view: #}
slides = [
    {'image': '/static/img1.jpg', 'caption': 'First Slide', 'description': 'Description'},
    {'image': '/static/img2.jpg', 'caption': 'Second Slide'},
    {'image': '/static/img3.jpg'},
]
```

**Options:**
- `controls` - Show prev/next buttons
- `indicators` - Show slide indicators
- `interval` - Auto-slide interval (ms)
- `fade` - Use fade transition
- `captions` - Show caption overlay

---

### 6. Dropdowns
Toggleable contextual overlays.

```django
{% skote_dropdown "Actions" items button_type="primary" %}

{# In view: #}
items = [
    {'text': 'Edit', 'url': '/edit/'},
    {'text': 'View Details', 'url': '/details/'},
    {'divider': True},
    {'text': 'Delete', 'url': '/delete/'},
]
```

**Options:**
- `split` - Split button style
- `direction` - `down`, `up`, `start`, `end`
- `alignment` - `start`, `end`

---

### 7. Modals
Dialog overlays.

```django
{% skote_modal "confirmModal" "Confirm Action" body="<p>Are you sure?</p>" %}
{% skote_modal "detailsModal" "Details" size="lg" centered=True footer_buttons=buttons %}

<!-- Trigger -->
<button data-bs-toggle="modal" data-bs-target="#confirmModal">Open Modal</button>

{# In view: #}
buttons = [
    {'text': 'Cancel', 'type': 'secondary', 'dismiss': True},
    {'text': 'Confirm', 'type': 'primary'},
]
```

---

### 8. Offcanvas
Hidden sidebars for navigation or content.

```django
{% skote_offcanvas "sidebar" "Menu" body=menu_content placement="start" %}

<!-- Trigger -->
<button data-bs-toggle="offcanvas" data-bs-target="#sidebar">Open Menu</button>
```

**Placements:** `start`, `end`, `top`, `bottom`

---

### 9. Progress Bars
Show task progress.

```django
{% skote_progress 75 type="success" %}
{% skote_progress 60 type="primary" striped=True animated=True %}
{% skote_progress 45 type="warning" label="45% Complete" height="25px" %}
```

---

### 10. Breadcrumbs
Navigation hierarchy.

```django
{% skote_breadcrumb items %}

{# In view: #}
items = [
    {'text': 'Home', 'url': '/'},
    {'text': 'Products', 'url': '/products/'},
    {'text': 'Detail'},  # Active item (no URL)
]
```

---

### 11. Placeholders
Loading skeletons.

```django
{% skote_placeholder lines=3 animation="wave" %}
{% skote_placeholder lines=5 animation="glow" size="lg" %}
```

---

### 12. Toasts
Push notifications.

```django
{% skote_toast "toast1" "Success" "Item saved successfully!" type="success" icon="bx bx-check-circle" %}

<!-- Trigger with JavaScript -->
<button onclick="new bootstrap.Toast(document.getElementById('toast1')).show()">
    Show Toast
</button>
```

**Positions:** `top-right`, `top-left`, `bottom-right`, `bottom-left`

---

### 13. Tabs
Organize content into tabs.

```django
{% skote_tabs tabs %}

{# In view: #}
tabs = [
    {'title': 'Profile', 'content': '<p>Profile content</p>', 'active': True, 'icon': 'bx bx-user'},
    {'title': 'Settings', 'content': '<p>Settings content</p>', 'icon': 'bx bx-cog'},
    {'title': 'Messages', 'content': '<p>Messages content</p>', 'icon': 'bx bx-envelope'},
]
```

**Options:**
- `pills` - Pill-style tabs
- `justified` - Full-width tabs
- `vertical` - Vertical layout

---

### 14. Accordions
Collapsible content panels.

```django
{% skote_accordion items %}

{# In view: #}
items = [
    {'title': 'Section 1', 'content': '<p>Content 1</p>', 'active': True},
    {'title': 'Section 2', 'content': '<p>Content 2</p>'},
    {'title': 'Section 3', 'content': '<p>Content 3</p>'},
]
```

**Options:**
- `flush` - Remove borders
- `always_open` - Allow multiple open sections

---

### 15. Icons
Vector icons from 4 libraries.

```django
{# Boxicons #}
{% skote_icon 'bx bx-home' size='24px' %}
{% skote_icon 'bx bx-user' color='primary' %}

{# Material Design Icons #}
{% skote_icon 'mdi mdi-account' size='2rem' color='#ff5722' %}

{# Font Awesome #}
{% skote_icon 'fas fa-heart' size='20px' color='danger' %}
```

---

### 16. Ratings
Star rating display.

```django
{% skote_rating 4.5 %}
{% skote_rating 3 max_rating=5 size="lg" color="warning" %}
```

---

### 17. Spinners
Loading indicators.

```django
{% skote_spinner type="border" color="primary" %}
{% skote_spinner type="grow" size="sm" color="success" %}
```

---

### 18. Avatars
User profile images with initials fallback.

```django
{% skote_avatar name="John Doe" size="lg" status="online" %}
{% skote_avatar image="/path/to/avatar.jpg" size="md" rounded=True %}
```

**Sizes:** `xs`, `sm`, `md`, `lg`, `xl`
**Status:** `online`, `offline`, `away`, `busy`

---

## Form Components

### 19. Text Input
```django
{% load skote_forms %}

{# With Django form #}
{% skote_input field=form.email %}

{# Manual #}
{% skote_input label="Email" name="email" input_type="email" required=True placeholder="Enter email" %}
```

---

### 20. Select Dropdown
```django
{% skote_select field=form.country %}

{# Manual #}
{% skote_select label="Country" name="country" choices=countries selected="us" %}
```

---

### 21. Textarea
```django
{% skote_textarea field=form.description %}
{% skote_textarea label="Comments" name="comments" rows=5 %}
```

---

### 22. Checkbox / Switch
```django
{% skote_checkbox field=form.agree %}
{% skote_checkbox label="Enable notifications" name="notify" switch=True checked=True %}
```

---

### 23. Radio Buttons
```django
{% skote_radio field=form.gender %}
{% skote_radio label="Size" name="size" choices=sizes inline=True %}
```

---

### 24. File Upload
```django
{% skote_file_upload field=form.document %}
{% skote_file_upload label="Upload Image" name="image" accept="image/*" %}
{% skote_file_upload label="Documents" name="docs" multiple=True %}
```

---

## Helper Components

### 25. Grid System
Use Bootstrap 5 grid classes directly:

```django
<div class="row">
    <div class="col-md-6 col-lg-4">Column 1</div>
    <div class="col-md-6 col-lg-4">Column 2</div>
    <div class="col-md-12 col-lg-4">Column 3</div>
</div>

{# Responsive utilities #}
<div class="row g-3">  <!-- Gap 3 -->
    <div class="col-sm-12 col-md-6 col-lg-3">...</div>
</div>
```

---

### 26. Images
```django
{# Responsive images #}
<img src="..." class="img-fluid" alt="...">

{# Thumbnails #}
<img src="..." class="img-thumbnail" alt="...">

{# Rounded #}
<img src="..." class="rounded" alt="...">
<img src="..." class="rounded-circle" alt="...">
```

---

### 27. Typography
```django
{# Headings #}
<h1 class="display-1">Display 1</h1>
<p class="lead">Lead paragraph</p>

{# Text utilities #}
<p class="text-primary">Primary text</p>
<p class="text-muted">Muted text</p>
<p class="fw-bold">Bold text</p>
<p class="fst-italic">Italic text</p>
<p class="text-decoration-underline">Underlined</p>

{# Lists #}
<ul class="list-unstyled">
    <li>Item 1</li>
    <li>Item 2</li>
</ul>
```

---

### 28. Colors
```django
{# Background colors #}
<div class="bg-primary text-white p-3">Primary background</div>
<div class="bg-success text-white p-3">Success background</div>

{# Text colors #}
<p class="text-primary">Primary text</p>
<p class="text-danger">Danger text</p>

{# Border colors #}
<div class="border border-primary p-3">Primary border</div>
```

**Available colors:** `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `white`, `muted`

---

### 29. Utilities
```django
{# Spacing (margin/padding) #}
<div class="mt-3">Margin top 3</div>
<div class="p-4">Padding all sides 4</div>
<div class="mx-auto">Center horizontally</div>

{# Display #}
<div class="d-none d-md-block">Hidden on mobile</div>
<div class="d-flex justify-content-between">Flex container</div>

{# Position #}
<div class="position-relative">
    <span class="position-absolute top-0 start-0">Top left</span>
</div>

{# Sizing #}
<div class="w-100">Width 100%</div>
<div class="h-50">Height 50%</div>

{# Shadows #}
<div class="shadow-sm">Small shadow</div>
<div class="shadow">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
```

---

### 30. Video
```django
{# Responsive video embed #}
<div class="ratio ratio-16x9">
    <iframe src="https://www.youtube.com/embed/..." allowfullscreen></iframe>
</div>

{# Other ratios: ratio-1x1, ratio-4x3, ratio-21x9 #}

{# HTML5 video #}
<video class="w-100" controls>
    <source src="movie.mp4" type="video/mp4">
</video>
```

---

## Advanced Components

### Lightbox
Requires: `{% static 'skote/libs/magnific-popup/magnific-popup.css' %}`

```django
{% block extra_css %}
<link href="{% static 'skote/libs/magnific-popup/magnific-popup.css' %}" rel="stylesheet">
{% endblock %}

<a href="/large-image.jpg" class="image-popup">
    <img src="/thumb.jpg" class="img-fluid" alt="">
</a>

{% block extra_js %}
<script src="{% static 'skote/libs/magnific-popup/jquery.magnific-popup.min.js' %}"></script>
<script>
$('.image-popup').magnificPopup({
    type: 'image',
    closeOnContentClick: true
});
</script>
{% endblock %}
```

---

### Range Slider
Requires: `{% static 'skote/libs/ion-rangeslider/ion.rangeSlider.min.js' %}`

```django
{% block extra_css %}
<link href="{% static 'skote/libs/ion-rangeslider/ion.rangeSlider.min.css' %}" rel="stylesheet">
{% endblock %}

<input type="text" id="range" name="range" value="">

{% block extra_js %}
<script src="{% static 'skote/libs/ion-rangeslider/ion.rangeSlider.min.js' %}"></script>
<script>
$("#range").ionRangeSlider({
    min: 0,
    max: 100,
    from: 50,
    grid: true
});
</script>
{% endblock %}
```

---

### Sweet Alert
Requires: `{% static 'skote/libs/sweetalert2/sweetalert2.min.js' %}`

```django
{% block extra_css %}
<link href="{% static 'skote/libs/sweetalert2/sweetalert2.min.css' %}" rel="stylesheet">
{% endblock %}

<button onclick="showAlert()">Show Alert</button>

{% block extra_js %}
<script src="{% static 'skote/libs/sweetalert2/sweetalert2.min.js' %}"></script>
<script>
function showAlert() {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#34c38f',
        cancelButtonColor: '#f46a6a',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire('Deleted!', 'Your file has been deleted.', 'success')
        }
    })
}
</script>
{% endblock %}
```

---

### Session Timeout
Requires: `{% static 'skote/libs/jquery-sessiontimeout/jquery.sessionTimeout.min.js' %}`

```django
{% block extra_js %}
<script src="{% static 'skote/libs/jquery-sessiontimeout/jquery.sessionTimeout.min.js' %}"></script>
<script>
$.sessionTimeout({
    keepAliveUrl: '/keep-alive/',
    logoutUrl: '/logout/',
    redirUrl: '/login/',
    warnAfter: 3000,  // 3 seconds for demo
    redirAfter: 5000,  // 5 seconds for demo
    message: 'Your session is about to expire.'
});
</script>
{% endblock %}
```

---

## Notification Component
Custom notification manager (Django messages integration):

```python
# views.py
from django.contrib import messages

def my_view(request):
    messages.success(request, 'Operation successful!')
    messages.error(request, 'An error occurred!')
    messages.warning(request, 'Warning message')
    messages.info(request, 'Information')
```

```django
{# In template #}
{% if messages %}
    <div class="position-fixed top-0 end-0 p-3" style="z-index: 11">
        {% for message in messages %}
        {% skote_toast "msg_{{ forloop.counter }}" "Notification" message.message type=message.tags %}
        <script>
            new bootstrap.Toast(document.getElementById('msg_{{ forloop.counter }}')).show();
        </script>
        {% endfor %}
    </div>
{% endif %}
```

---

## Component Combinations

### Dashboard Card with Progress
```django
<div class="card">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="card-title mb-0">Project Progress</h5>
            {% skote_badge "In Progress" type="warning" %}
        </div>
        <p class="text-muted">Task completion rate</p>
        {% skote_progress 75 type="success" striped=True animated=True %}
        <div class="mt-3">
            <span class="text-muted">75% Complete</span>
        </div>
    </div>
</div>
```

### Stats Card
```django
<div class="card">
    <div class="card-body">
        <div class="d-flex">
            <div class="flex-grow-1">
                <p class="text-muted fw-medium mb-2">Total Sales</p>
                <h4 class="mb-0">$45,320</h4>
            </div>
            <div class="flex-shrink-0 align-self-center">
                <div class="avatar-sm rounded-circle bg-primary">
                    <span class="avatar-title rounded-circle bg-primary">
                        {% skote_icon 'bx bx-dollar' size='24px' color='white' %}
                    </span>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Action Dropdown with Icons
```django
{% skote_dropdown "Actions" items %}

{# In view: #}
items = [
    {'text': '<i class="bx bx-pencil me-2"></i>Edit', 'url': '/edit/'},
    {'text': '<i class="bx bx-copy me-2"></i>Duplicate', 'url': '/duplicate/'},
    {'divider': True},
    {'text': '<i class="bx bx-trash me-2 text-danger"></i>Delete', 'url': '/delete/'},
]
```

---

## Best Practices

1. **Always load the appropriate tag library:**
   ```django
   {% load skote_components %}  {# For UI components #}
   {% load skote_forms %}       {# For form components #}
   ```

2. **Use context variables for dynamic data:**
   ```python
   # views.py
   context = {
       'slides': [...],
       'tabs': [...],
       'items': [...],
   }
   ```

3. **Combine components for rich interfaces:**
   - Cards + Tabs for tabbed content
   - Modals + Forms for data entry
   - Dropdowns + Badges for actions with status

4. **Leverage Bootstrap utilities:**
   - Spacing: `mt-3`, `p-4`, `mx-auto`
   - Display: `d-flex`, `d-none d-md-block`
   - Colors: `text-primary`, `bg-success`

5. **Use appropriate sizes:**
   - Buttons: `sm`, `lg`
   - Modals: `sm`, `lg`, `xl`
   - Avatars: `xs`, `sm`, `md`, `lg`, `xl`

This reference covers all 30+ components in the Skote library. For detailed examples, see EXAMPLES.md.
