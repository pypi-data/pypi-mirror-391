# Tables and Advanced Forms Guide

Complete guide for using Tables and Advanced Form components in Skote Django Component Library.

## Table of Contents
1. [Tables](#tables)
2. [Advanced Forms](#advanced-forms)
3. [Icons](#icons)
4. [Complete Examples](#complete-examples)

---

## TABLES

### 1. Basic Tables

Simple, styled tables with Bootstrap classes.

```django
{% load skote_components %}

{# Basic table #}
{% skote_table headers rows %}

{# Striped table #}
{% skote_table headers rows striped=True %}

{# With borders and hover #}
{% skote_table headers rows striped=True bordered=True hover=True %}

{# Small table #}
{% skote_table headers rows small=True %}
```

**In your view:**
```python
def table_view(request):
    headers = ['#', 'Name', 'Email', 'Role', 'Status', 'Actions']

    rows = [
        ['1', 'John Doe', 'john@example.com', 'Admin',
         '<span class="badge bg-success">Active</span>',
         '''{% skote_table_actions edit_url="/edit/1/" delete_url="/delete/1/" %}'''],

        ['2', 'Jane Smith', 'jane@example.com', 'User',
         '<span class="badge bg-warning">Pending</span>',
         '''{% skote_table_actions edit_url="/edit/2/" delete_url="/delete/2/" %}'''],
    ]

    context = {'headers': headers, 'rows': rows}
    return render(request, 'table_page.html', context)
```

**Table Options:**
- `striped` - Zebra-striping
- `bordered` - Borders on all sides
- `hover` - Hover state on rows
- `small` - Compact table
- `responsive` - Responsive wrapper (default: True)
- `table_class` - Additional CSS classes

---

### 2. DataTables (Advanced)

Interactive tables with sorting, searching, and pagination.

**Template:**
```django
{% load skote_components %}

{% block extra_css %}
<link href="{% static 'skote/libs/datatables.net-bs4/css/dataTables.bootstrap4.min.css' %}" rel="stylesheet">
<link href="{% static 'skote/libs/datatables.net-responsive-bs4/css/responsive.bootstrap4.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h4 class="card-title">Users Table</h4>
        {% skote_datatable "usersTable" headers %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/datatables.net/js/jquery.dataTables.min.js' %}"></script>
<script src="{% static 'skote/libs/datatables.net-bs4/js/dataTables.bootstrap4.min.js' %}"></script>
<script src="{% static 'skote/libs/datatables.net-responsive/js/dataTables.responsive.min.js' %}"></script>
<script src="{% static 'skote/libs/datatables.net-responsive-bs4/js/responsive.bootstrap4.min.js' %}"></script>
{% endblock %}
```

**View:**
```python
def datatable_view(request):
    headers = ['ID', 'Name', 'Email', 'Role', 'Status', 'Actions']

    context = {'headers': headers}
    return render(request, 'datatable_page.html', context)
```

**With AJAX Data Source:**
```django
{% skote_datatable "usersTable" headers data_url="/api/users/" %}
```

**API Endpoint (views.py):**
```python
from django.http import JsonResponse

def users_api(request):
    users = User.objects.all()

    data = {
        'data': [[
            user.id,
            user.get_full_name(),
            user.email,
            user.role,
            f'<span class="badge bg-success">Active</span>' if user.is_active else '<span class="badge bg-danger">Inactive</span>',
            f'<a href="/edit/{user.id}/" class="btn btn-sm btn-primary"><i class="bx bx-edit"></i></a>'
        ] for user in users]
    }

    return JsonResponse(data)
```

**DataTable Options:**
- `ordering` - Enable sorting (default: True)
- `searching` - Enable search box (default: True)
- `paging` - Enable pagination (default: True)
- `page_length` - Rows per page (default: 10)
- `data_url` - AJAX data source URL

---

### 3. Table Actions

Render action buttons for table rows.

```django
{% load skote_components %}

{# Basic actions #}
{% skote_table_actions edit_url="/edit/1/" delete_url="/delete/1/" view_url="/view/1/" %}

{# Only edit and delete #}
{% skote_table_actions edit_url="/edit/1/" delete_url="/delete/1/" %}

{# Custom actions #}
{% skote_table_actions edit_url="/edit/1/" custom_actions=custom_actions %}
```

**In view:**
```python
custom_actions = [
    {'url': '/clone/1/', 'icon': 'bx bx-copy', 'class': 'btn-outline-info', 'text': 'Clone'},
    {'url': '/export/1/', 'icon': 'bx bx-download', 'class': 'btn-outline-success', 'text': 'Export'},
]
context['custom_actions'] = custom_actions
```

---

### 4. Responsive Tables

Tables automatically responsive with horizontal scroll on small screens.

```django
{# Responsive by default #}
{% skote_table headers rows striped=True %}

{# Disable responsive wrapper #}
{% skote_table headers rows responsive=False %}
```

---

### 5. Editable Tables

Inline editing with x-editable library.

**Template:**
```django
{% block extra_css %}
<link href="{% static 'skote/libs/bootstrap-editable/css/bootstrap-editable.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<table class="table table-striped">
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td><a href="#" class="editable" data-pk="{{ user.id }}" data-name="name" data-type="text">{{ user.name }}</a></td>
            <td><a href="#" class="editable" data-pk="{{ user.id }}" data-name="email" data-type="email">{{ user.email }}</a></td>
            <td>
                <a href="#" class="editable" data-pk="{{ user.id }}" data-name="role" data-type="select" data-source='[{"value":"admin","text":"Admin"},{"value":"user","text":"User"}]'>
                    {{ user.role }}
                </a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/bootstrap-editable/js/bootstrap-editable.min.js' %}"></script>
<script>
$('.editable').editable({
    url: '/update-user/',
    title: 'Edit field',
    success: function(response) {
        if(response.status == 'success') {
            toastr.success('Updated successfully');
        }
    }
});
</script>
{% endblock %}
```

---

## ADVANCED FORMS

### 1. Form Validation

Bootstrap 5 client-side validation.

```django
{% load skote_forms %}

<form class="{% skote_form_validation_class %}" novalidate method="post">
    {% csrf_token %}

    {% skote_input label="Username" name="username" required=True %}
    {% skote_input label="Email" name="email" input_type="email" required=True %}
    {% skote_input label="Password" name="password" input_type="password" required=True %}

    <button type="submit" class="btn btn-primary">Submit</button>
</form>

<script>
// Bootstrap validation
(function() {
    'use strict';
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();
</script>
```

---

### 2. Form Wizard

Multi-step forms with progress indicator.

```django
{% load skote_forms %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h4 class="card-title mb-4">Registration Wizard</h4>

        {% skote_form_wizard steps %}

        <div class="d-flex justify-content-between mt-4">
            <button type="button" class="btn btn-secondary" id="prevBtn">Previous</button>
            <button type="button" class="btn btn-primary" id="nextBtn">Next</button>
        </div>
    </div>
</div>
{% endblock %}
```

**In view:**
```python
def wizard_view(request):
    steps = [
        {
            'title': 'Personal Info',
            'icon': 'bx bx-user',
            'content': '''
                <div class="mb-3">
                    <label class="form-label">First Name</label>
                    <input type="text" class="form-control" name="first_name" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Last Name</label>
                    <input type="text" class="form-control" name="last_name" required>
                </div>
            '''
        },
        {
            'title': 'Contact Info',
            'icon': 'bx bx-envelope',
            'content': '''
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" name="email" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-control" name="phone">
                </div>
            '''
        },
        {
            'title': 'Confirmation',
            'icon': 'bx bx-check-circle',
            'content': '''
                <p>Please review your information and submit.</p>
                <button type="submit" class="btn btn-success">Submit</button>
            '''
        }
    ]

    context = {'steps': steps}
    return render(request, 'wizard.html', context)
```

**Wizard Navigation JavaScript:**
```javascript
let currentStep = 1;
const totalSteps = $('.tab-pane').length;

$('#nextBtn').click(function() {
    if (currentStep < totalSteps) {
        currentStep++;
        $(`.nav-link[href="#step${currentStep}"]`).tab('show');
    }
    updateButtons();
});

$('#prevBtn').click(function() {
    if (currentStep > 1) {
        currentStep--;
        $(`.nav-link[href="#step${currentStep}"]`).tab('show');
    }
    updateButtons();
});

function updateButtons() {
    $('#prevBtn').prop('disabled', currentStep === 1);
    $('#nextBtn').toggle(currentStep !== totalSteps);
}
```

---

### 3. Date Picker

Date selection with calendar popup.

```django
{% load skote_forms %}

{% block extra_css %}
<link href="{% static 'skote/libs/bootstrap-datepicker/css/bootstrap-datepicker.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
{% skote_datepicker "start_date" label="Start Date" format="yyyy-mm-dd" %}
{% skote_datepicker "end_date" label="End Date" min_date="today" %}
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/bootstrap-datepicker/js/bootstrap-datepicker.min.js' %}"></script>
<script>
$('.datepicker').datepicker({
    autoclose: true,
    todayHighlight: true
});
</script>
{% endblock %}
```

---

### 4. Color Picker

Color selection tool.

```django
{% load skote_forms %}

{% block extra_css %}
<link href="{% static 'skote/libs/@simonwep/pickr/themes/classic.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
{% skote_colorpicker "theme_color" label="Theme Color" value="#556ee6" %}
{% skote_colorpicker "bg_color" label="Background Color" value="#f8f9fa" %}
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/@simonwep/pickr/pickr.min.js' %}"></script>
<script>
$('.colorpicker').each(function() {
    const input = this;
    Pickr.create({
        el: input,
        theme: 'classic',
        default: $(input).val(),
        components: {
            preview: true,
            opacity: true,
            hue: true,
            interaction: {
                input: true,
                save: true
            }
        }
    }).on('save', (color) => {
        $(input).val(color.toHEXA().toString());
    });
});
</script>
{% endblock %}
```

---

### 5. Form Repeater

Dynamic add/remove form fields.

```django
{% load skote_forms %}

{% block extra_css %}
<link href="{% static 'skote/libs/jquery.repeater/jquery.repeater.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<form method="post">
    {% csrf_token %}

    {% skote_repeater field_template add_button_text="Add Member" %}

</form>
{% endblock %}
```

**In view:**
```python
field_template = '''
<div class="row">
    <div class="col-md-4">
        <input type="text" class="form-control" name="member_name[]" placeholder="Name">
    </div>
    <div class="col-md-4">
        <input type="email" class="form-control" name="member_email[]" placeholder="Email">
    </div>
    <div class="col-md-4">
        <input type="tel" class="form-control" name="member_phone[]" placeholder="Phone">
    </div>
</div>
'''
context['field_template'] = field_template
```

**JavaScript:**
```javascript
{% block extra_js %}
<script src="{% static 'skote/libs/jquery.repeater/jquery.repeater.min.js' %}"></script>
<script>
$('.form-repeater').repeater({
    show: function () {
        $(this).slideDown();
    },
    hide: function (deleteElement) {
        if(confirm('Are you sure you want to delete this?')) {
            $(this).slideUp(deleteElement);
        }
    }
});

// Simpler version without library
$('.repeater-add').click(function() {
    const item = $('.repeater-item:first').clone();
    item.find('input, select, textarea').val('');
    $('.repeater-items').append(item);
});

$(document).on('click', '.repeater-remove', function() {
    if($('.repeater-item').length > 1) {
        $(this).closest('.repeater-item').remove();
    }
});
</script>
{% endblock %}
```

---

### 6. Input Mask

Format input values (phone, date, credit card, etc.).

```django
{% load skote_forms %}

{% block extra_css %}
<link href="{% static 'skote/libs/inputmask/inputmask.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
{# Phone mask #}
{% skote_input_mask "phone" label="Phone" mask="(999) 999-9999" placeholder="(___) ___-____" %}

{# Date mask #}
{% skote_input_mask "date" label="Date" mask="99/99/9999" placeholder="MM/DD/YYYY" %}

{# Credit card #}
{% skote_input_mask "card" label="Credit Card" mask="9999-9999-9999-9999" %}

{# SSN #}
{% skote_input_mask "ssn" label="SSN" mask="999-99-9999" %}
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/inputmask/inputmask.min.js' %}"></script>
<script>
$('.input-mask').each(function() {
    const mask = $(this).data('inputmask');
    Inputmask(mask).mask(this);
});
</script>
{% endblock %}
```

---

### 7. WYSIWYG Editors

Rich text editors for content creation.

**TinyMCE:**
```django
{% block extra_css %}
{% endblock %}

{% block content %}
<div class="mb-3">
    <label class="form-label">Content</label>
    <textarea id="editor" name="content" class="form-control"></textarea>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/tinymce/tinymce.min.js' %}"></script>
<script>
tinymce.init({
    selector: '#editor',
    height: 300,
    menubar: false,
    plugins: 'lists link image table code',
    toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link image | code'
});
</script>
{% endblock %}
```

**CKEditor:**
```django
{% block extra_js %}
<script src="{% static 'skote/libs/@ckeditor/ckeditor5-build-classic/build/ckeditor.js' %}"></script>
<script>
ClassicEditor
    .create(document.querySelector('#editor'))
    .catch(error => {
        console.error(error);
    });
</script>
{% endblock %}
```

---

## ICONS

All 4 icon libraries are included in the Skote theme.

### Boxicons
```django
{% load skote_components %}

{% skote_icon 'bx bx-home' %}
{% skote_icon 'bx bx-user' size='24px' %}
{% skote_icon 'bx bx-heart' color='danger' %}
{% skote_icon 'bx bxs-star' color='#FFD700' %}
```

**Common Boxicons:**
- `bx bx-home` - Home
- `bx bx-user` - User
- `bx bx-cog` - Settings
- `bx bx-search` - Search
- `bx bx-edit` - Edit
- `bx bx-trash` - Delete
- `bx bx-plus` - Add
- `bx bx-check` - Check
- `bx bx-x` - Close
- `bx bx-envelope` - Email
- `bx bx-phone` - Phone
- `bx bx-calendar` - Calendar
- `bx bx-download` - Download
- `bx bx-upload` - Upload
- `bxs-star` - Filled star (bxs = solid)

View all: [Boxicons](https://boxicons.com/)

### Material Design Icons
```django
{% skote_icon 'mdi mdi-account' %}
{% skote_icon 'mdi mdi-email' size='20px' color='primary' %}
```

**Common MDI:**
- `mdi mdi-account` - Account
- `mdi mdi-home` - Home
- `mdi mdi-cog` - Settings
- `mdi mdi-delete` - Delete
- `mdi mdi-pencil` - Edit
- `mdi mdi-check` - Check
- `mdi mdi-close` - Close

View all: [Material Design Icons](https://materialdesignicons.com/)

### Font Awesome
```django
{% skote_icon 'fas fa-heart' %}
{% skote_icon 'far fa-envelope' size='18px' %}
```

**Styles:**
- `fas` - Solid
- `far` - Regular
- `fab` - Brands

View all: [Font Awesome](https://fontawesome.com/icons)

### Dripicons
```django
<i class="dripicons-home"></i>
<i class="dripicons-user"></i>
```

---

## COMPLETE EXAMPLES

### Example 1: User Management Table with Actions

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
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="card-title mb-0">Users</h4>
                    {% skote_button "Add User" type="primary" icon="bx bx-plus" href="/users/create/" %}
                </div>

                {% skote_datatable "usersTable" headers %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/datatables.net/js/jquery.dataTables.min.js' %}"></script>
<script src="{% static 'skote/libs/datatables.net-bs4/js/dataTables.bootstrap4.min.js' %}"></script>
<script>
$('#usersTable').DataTable({
    ajax: '/api/users/',
    columns: [
        { data: 'id' },
        { data: 'name' },
        { data: 'email' },
        { data: 'role' },
        { data: 'status' },
        {
            data: null,
            render: function(data, type, row) {
                return `
                    <div class="btn-group">
                        <a href="/users/edit/${row.id}/" class="btn btn-sm btn-outline-primary">
                            <i class="bx bx-edit"></i>
                        </a>
                        <button onclick="deleteUser(${row.id})" class="btn btn-sm btn-outline-danger">
                            <i class="bx bx-trash"></i>
                        </button>
                    </div>
                `;
            }
        }
    ]
});

function deleteUser(id) {
    if(confirm('Are you sure?')) {
        // Delete logic
    }
}
</script>
{% endblock %}
```

### Example 2: Multi-Step Registration Form

```django
{% extends 'base/base.html' %}
{% load skote_forms skote_components %}

{% block extra_css %}
<link href="{% static 'skote/libs/bootstrap-datepicker/css/bootstrap-datepicker.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Company Registration</h4>

                <form class="{% skote_form_validation_class %}" method="post" novalidate>
                    {% csrf_token %}

                    {% skote_form_wizard steps %}

                    <div class="d-flex justify-content-between mt-4">
                        <button type="button" class="btn btn-secondary" id="prevBtn">Previous</button>
                        <button type="submit" class="btn btn-primary" id="submitBtn" style="display:none;">Submit</button>
                        <button type="button" class="btn btn-primary" id="nextBtn">Next</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/bootstrap-datepicker/js/bootstrap-datepicker.min.js' %}"></script>
<script>
$('.datepicker').datepicker({ autoclose: true });

let currentStep = 1;
const totalSteps = 3;

$('#nextBtn').click(function() {
    if (validateStep(currentStep)) {
        if (currentStep < totalSteps) {
            currentStep++;
            $(`.nav-link[href="#step${currentStep}"]`).tab('show');
        }
        updateButtons();
    }
});

$('#prevBtn').click(function() {
    if (currentStep > 1) {
        currentStep--;
        $(`.nav-link[href="#step${currentStep}"]`).tab('show');
    }
    updateButtons();
});

function updateButtons() {
    $('#prevBtn').prop('disabled', currentStep === 1);
    $('#nextBtn').toggle(currentStep !== totalSteps);
    $('#submitBtn').toggle(currentStep === totalSteps);
}

function validateStep(step) {
    const form = document.querySelector('.needs-validation');
    const currentPane = document.querySelector(`#step${step}`);
    const inputs = currentPane.querySelectorAll('input[required], select[required]');

    let valid = true;
    inputs.forEach(input => {
        if (!input.checkValidity()) {
            valid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return valid;
}
</script>
{% endblock %}
```

### Example 3: Advanced Form with All Components

```django
{% extends 'base/base.html' %}
{% load skote_forms skote_components %}

{% block extra_css %}
<link href="{% static 'skote/libs/bootstrap-datepicker/css/bootstrap-datepicker.min.css' %}" rel="stylesheet">
<link href="{% static 'skote/libs/@simonwep/pickr/themes/classic.min.css' %}" rel="stylesheet">
<link href="{% static 'skote/libs/inputmask/inputmask.min.css' %}" rel="stylesheet">
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h4 class="card-title mb-4">Project Form</h4>

                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}

                    <div class="row">
                        <div class="col-md-6">
                            {% skote_input label="Project Name" name="name" required=True %}
                        </div>
                        <div class="col-md-6">
                            {% skote_select label="Status" name="status" choices=statuses required=True %}
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6">
                            {% skote_datepicker "start_date" label="Start Date" %}
                        </div>
                        <div class="col-md-6">
                            {% skote_datepicker "end_date" label="End Date" %}
                        </div>
                    </div>

                    {% skote_textarea label="Description" name="description" rows=4 %}

                    <div class="row">
                        <div class="col-md-6">
                            {% skote_colorpicker "theme_color" label="Theme Color" %}
                        </div>
                        <div class="col-md-6">
                            {% skote_input_mask "budget" label="Budget" mask="$999,999,999" %}
                        </div>
                    </div>

                    <h5 class="font-size-14 mb-3">Team Members</h5>
                    {% skote_repeater member_template add_button_text="Add Member" %}

                    <div class="mt-4">
                        {% skote_button "Save Project" type="primary" icon="bx bx-save" %}
                        {% skote_button "Cancel" type="secondary" outline=True href="/" %}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'skote/libs/bootstrap-datepicker/js/bootstrap-datepicker.min.js' %}"></script>
<script src="{% static 'skote/libs/@simonwep/pickr/pickr.min.js' %}"></script>
<script src="{% static 'skote/libs/inputmask/inputmask.min.js' %}"></script>
<script>
$('.datepicker').datepicker({ autoclose: true, todayHighlight: true });
$('.input-mask').each(function() {
    Inputmask($(this).data('inputmask')).mask(this);
});

// Color picker
const pickr = Pickr.create({
    el: '.colorpicker',
    theme: 'classic',
    default: '#556ee6',
    components: { preview: true, hue: true, interaction: { input: true, save: true } }
});

// Repeater
$('.repeater-add').click(function() {
    const item = $('.repeater-item:first').clone();
    item.find('input').val('');
    $('.repeater-items').append(item);
});

$(document).on('click', '.repeater-remove', function() {
    if($('.repeater-item').length > 1) {
        $(this).closest('.repeater-item').remove();
    }
});
</script>
{% endblock %}
```

---

## Summary

**Tables (4 types):**
- ✅ Basic Tables
- ✅ DataTables (with AJAX)
- ✅ Responsive Tables
- ✅ Editable Tables

**Forms (10+ components):**
- ✅ Form Elements (input, select, textarea, checkbox, radio, file)
- ✅ Form Validation
- ✅ Form Wizard (multi-step)
- ✅ Form Advanced (datepicker, colorpicker)
- ✅ Form Repeater (dynamic fields)
- ✅ Form Mask (input formatting)
- ✅ Form Editors (WYSIWYG)

**Icons (4 libraries):**
- ✅ Boxicons
- ✅ Material Design Icons
- ✅ Dripicons
- ✅ Font Awesome

All components are production-ready and fully integrated with Django!
