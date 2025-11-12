"""
Skote Form Component Template Tags

Usage in templates:
    {% load skote_forms %}
"""

from django import template
from django.forms import BoundField
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.inclusion_tag('components/forms/input.html')
def skote_input(field=None, label=None, placeholder=None, help_text=None,
                input_type='text', required=False, name=None, value=None,
                input_class='', readonly=False, disabled=False):
    """
    Render a form input field

    Args:
        field: Django form field (BoundField)
        label: Field label
        placeholder: Placeholder text
        help_text: Help text below field
        input_type: Input type (text, email, password, number, etc.)
        required: Required field
        name: Input name attribute
        value: Input value
        input_class: Additional CSS classes for input
        readonly: Readonly attribute
        disabled: Disabled attribute

    Usage:
        {% skote_input field=form.email %}
        {% skote_input label="Email" name="email" input_type="email" required=True %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'value': field.value(),
            'errors': field.errors,
            'help_text': field.help_text,
            'required': field.field.required,
            'input_class': input_class,
        }
    return {
        'label': label,
        'placeholder': placeholder,
        'help_text': help_text,
        'input_type': input_type,
        'required': required,
        'name': name,
        'value': value or '',
        'input_class': input_class,
        'readonly': readonly,
        'disabled': disabled,
    }


@register.inclusion_tag('components/forms/select.html')
def skote_select(field=None, label=None, choices=None, help_text=None,
                 required=False, name=None, selected=None, select_class=''):
    """
    Render a select dropdown

    Args:
        field: Django form field (BoundField)
        label: Field label
        choices: List of tuples [(value, label), ...]
        help_text: Help text below field
        required: Required field
        name: Select name attribute
        selected: Selected value
        select_class: Additional CSS classes

    Usage:
        {% skote_select field=form.country %}
        {% skote_select label="Country" choices=countries name="country" %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'choices': field.field.choices,
            'selected': field.value(),
            'errors': field.errors,
            'help_text': field.help_text,
            'required': field.field.required,
            'select_class': select_class,
        }
    return {
        'label': label,
        'choices': choices or [],
        'help_text': help_text,
        'required': required,
        'name': name,
        'selected': selected,
        'select_class': select_class,
    }


@register.inclusion_tag('components/forms/textarea.html')
def skote_textarea(field=None, label=None, placeholder=None, help_text=None,
                   required=False, name=None, value=None, rows=3,
                   textarea_class='', readonly=False, disabled=False):
    """
    Render a textarea field

    Args:
        field: Django form field (BoundField)
        label: Field label
        placeholder: Placeholder text
        help_text: Help text below field
        required: Required field
        name: Textarea name attribute
        value: Textarea value
        rows: Number of rows
        textarea_class: Additional CSS classes
        readonly: Readonly attribute
        disabled: Disabled attribute

    Usage:
        {% skote_textarea field=form.description %}
        {% skote_textarea label="Description" name="description" rows=5 %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'value': field.value(),
            'errors': field.errors,
            'help_text': field.help_text,
            'required': field.field.required,
            'rows': rows,
            'textarea_class': textarea_class,
        }
    return {
        'label': label,
        'placeholder': placeholder,
        'help_text': help_text,
        'required': required,
        'name': name,
        'value': value or '',
        'rows': rows,
        'textarea_class': textarea_class,
        'readonly': readonly,
        'disabled': disabled,
    }


@register.inclusion_tag('components/forms/checkbox.html')
def skote_checkbox(field=None, label=None, name=None, checked=False,
                   value='1', help_text=None, switch=False, checkbox_class=''):
    """
    Render a checkbox or switch

    Args:
        field: Django form field (BoundField)
        label: Checkbox label
        name: Checkbox name attribute
        checked: Checked state
        value: Checkbox value
        help_text: Help text
        switch: Render as switch instead of checkbox
        checkbox_class: Additional CSS classes

    Usage:
        {% skote_checkbox field=form.agree %}
        {% skote_checkbox label="Remember me" name="remember" switch=True %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'checked': field.value(),
            'value': '1',
            'errors': field.errors,
            'help_text': field.help_text,
            'switch': switch,
            'checkbox_class': checkbox_class,
        }
    return {
        'label': label,
        'name': name,
        'checked': checked,
        'value': value,
        'help_text': help_text,
        'switch': switch,
        'checkbox_class': checkbox_class,
    }


@register.inclusion_tag('components/forms/radio.html')
def skote_radio(field=None, label=None, name=None, choices=None,
                selected=None, inline=False, help_text=None):
    """
    Render radio buttons

    Args:
        field: Django form field (BoundField)
        label: Field label
        name: Radio name attribute
        choices: List of tuples [(value, label), ...]
        selected: Selected value
        inline: Display inline
        help_text: Help text

    Usage:
        {% skote_radio field=form.gender %}
        {% skote_radio label="Size" choices=sizes name="size" inline=True %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'choices': field.field.choices,
            'selected': field.value(),
            'errors': field.errors,
            'help_text': field.help_text,
            'inline': inline,
        }
    return {
        'label': label,
        'name': name,
        'choices': choices or [],
        'selected': selected,
        'help_text': help_text,
        'inline': inline,
    }


@register.inclusion_tag('components/forms/file_upload.html')
def skote_file_upload(field=None, label=None, name=None, help_text=None,
                      required=False, accept=None, multiple=False):
    """
    Render a file upload field

    Args:
        field: Django form field (BoundField)
        label: Field label
        name: Input name attribute
        help_text: Help text
        required: Required field
        accept: Accepted file types (e.g., 'image/*', '.pdf,.doc')
        multiple: Allow multiple files

    Usage:
        {% skote_file_upload field=form.document %}
        {% skote_file_upload label="Upload Image" accept="image/*" %}
    """
    if field and isinstance(field, BoundField):
        return {
            'field': field,
            'label': field.label,
            'name': field.html_name,
            'errors': field.errors,
            'help_text': field.help_text,
            'required': field.field.required,
            'accept': accept,
            'multiple': multiple,
        }
    return {
        'label': label,
        'name': name,
        'help_text': help_text,
        'required': required,
        'accept': accept,
        'multiple': multiple,
    }


# ADVANCED FORM COMPONENTS

@register.simple_tag
def skote_form_wizard(steps, wizard_id=None):
    """
    Render a form wizard with steps

    Args:
        steps: List of dicts with 'title', 'icon', 'content'
        wizard_id: Unique wizard ID

    Usage:
        {% skote_form_wizard steps %}
    """
    import uuid
    if not wizard_id:
        wizard_id = f'wizard_{uuid.uuid4().hex[:8]}'

    html = f'<div id="{wizard_id}" class="form-wizard">'

    # Steps indicator
    html += '<ul class="nav nav-pills nav-justified form-wizard-header mb-4">'
    for i, step in enumerate(steps, 1):
        active = 'active' if i == 1 else ''
        html += f'''
        <li class="nav-item">
            <a href="#step{i}" data-bs-toggle="tab" data-toggle="tab" class="nav-link {active}">
                <i class="{step.get('icon', 'bx bx-check-circle')} d-block check-nav-icon mt-4 mb-2"></i>
                <p class="fw-bold mb-4">{step.get('title', f'Step {i}')}</p>
            </a>
        </li>
        '''
    html += '</ul>'

    # Step content
    html += '<div class="tab-content">'
    for i, step in enumerate(steps, 1):
        active = 'show active' if i == 1 else ''
        html += f'''
        <div class="tab-pane {active}" id="step{i}">
            {step.get('content', '')}
        </div>
        '''
    html += '</div>'
    html += '</div>'

    return mark_safe(html)


@register.simple_tag
def skote_datepicker(name, label=None, value='', input_id=None, format='mm/dd/yyyy',
                    min_date=None, max_date=None):
    """
    Render a date picker input

    Args:
        name: Input name
        label: Field label
        value: Initial value
        input_id: Input ID
        format: Date format
        min_date: Minimum date
        max_date: Maximum date

    Usage:
        {% skote_datepicker "start_date" label="Start Date" %}
    """
    import uuid
    if not input_id:
        input_id = f'datepicker_{uuid.uuid4().hex[:8]}'

    html = '<div class="mb-3">'
    if label:
        html += f'<label for="{input_id}" class="form-label">{label}</label>'

    html += f'''
    <input type="text" class="form-control datepicker" id="{input_id}" name="{name}"
           value="{value}" data-date-format="{format}"
           {f'data-date-min-date="{min_date}"' if min_date else ''}
           {f'data-date-max-date="{max_date}"' if max_date else ''}>
    '''
    html += '</div>'

    return mark_safe(html)


@register.simple_tag
def skote_colorpicker(name, label=None, value='#556ee6', input_id=None):
    """
    Render a color picker input

    Args:
        name: Input name
        label: Field label
        value: Initial color value
        input_id: Input ID

    Usage:
        {% skote_colorpicker "theme_color" label="Theme Color" %}
    """
    import uuid
    if not input_id:
        input_id = f'colorpicker_{uuid.uuid4().hex[:8]}'

    html = '<div class="mb-3">'
    if label:
        html += f'<label for="{input_id}" class="form-label">{label}</label>'

    html += f'''
    <input type="text" class="form-control colorpicker" id="{input_id}"
           name="{name}" value="{value}">
    '''
    html += '</div>'

    return mark_safe(html)


@register.simple_tag
def skote_repeater(template_html, repeater_id=None, add_button_text="Add Item",
                  remove_button_text="Remove"):
    """
    Render a form repeater (dynamic add/remove fields)

    Args:
        template_html: HTML template for each repeated item
        repeater_id: Unique repeater ID
        add_button_text: Text for add button
        remove_button_text: Text for remove button

    Usage:
        {% skote_repeater template_html %}
    """
    import uuid
    if not repeater_id:
        repeater_id = f'repeater_{uuid.uuid4().hex[:8]}'

    html = f'''
    <div id="{repeater_id}" class="form-repeater">
        <div class="repeater-items">
            <div class="repeater-item mb-3">
                {template_html}
                <button type="button" class="btn btn-danger btn-sm repeater-remove">
                    {remove_button_text}
                </button>
            </div>
        </div>
        <button type="button" class="btn btn-success btn-sm repeater-add">
            <i class="bx bx-plus"></i> {add_button_text}
        </button>
    </div>
    '''

    return mark_safe(html)


@register.simple_tag
def skote_form_validation_class():
    """
    Add Bootstrap form validation classes

    Usage in form tag:
        <form class="{% skote_form_validation_class %}" novalidate>
    """
    return 'needs-validation'


@register.simple_tag
def skote_input_mask(name, label=None, mask='', placeholder='', input_id=None):
    """
    Render an input with mask (phone, date, etc.)

    Args:
        name: Input name
        label: Field label
        mask: Input mask pattern
        placeholder: Placeholder
        input_id: Input ID

    Usage:
        {% skote_input_mask "phone" label="Phone" mask="(999) 999-9999" %}
    """
    import uuid
    if not input_id:
        input_id = f'masked_{uuid.uuid4().hex[:8]}'

    html = '<div class="mb-3">'
    if label:
        html += f'<label for="{input_id}" class="form-label">{label}</label>'

    html += f'''
    <input type="text" class="form-control input-mask" id="{input_id}"
           name="{name}" data-inputmask="'mask': '{mask}'" placeholder="{placeholder}">
    '''
    html += '</div>'

    return mark_safe(html)
