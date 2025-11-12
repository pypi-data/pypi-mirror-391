"""
Skote Component Template Tags

Usage in templates:
    {% load skote_components %}
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('components/ui/alert.html')
def skote_alert(message, type='primary', dismissible=True, icon=None):
    """
    Render a Bootstrap alert component

    Args:
        message: The alert message text
        type: Alert type (primary, secondary, success, danger, warning, info, light, dark)
        dismissible: Whether the alert can be dismissed
        icon: Optional icon class (e.g., 'bx bx-info-circle')

    Usage:
        {% skote_alert "This is an alert message" type="success" %}
        {% skote_alert "Warning!" type="warning" icon="bx bx-error" %}
    """
    return {
        'message': message,
        'type': type,
        'dismissible': dismissible,
        'icon': icon,
    }


@register.inclusion_tag('components/ui/card.html')
def skote_card(title=None, subtitle=None, content=None, footer=None,
               header_class='', body_class='', footer_class='', card_class=''):
    """
    Render a card component

    Args:
        title: Card title
        subtitle: Card subtitle
        content: Card body content (HTML safe)
        footer: Card footer content
        header_class: Additional classes for card header
        body_class: Additional classes for card body
        footer_class: Additional classes for card footer
        card_class: Additional classes for the card

    Usage:
        {% skote_card title="Card Title" content="Card content here" %}
    """
    return {
        'title': title,
        'subtitle': subtitle,
        'content': mark_safe(content) if content else None,
        'footer': footer,
        'header_class': header_class,
        'body_class': body_class,
        'footer_class': footer_class,
        'card_class': card_class,
    }


@register.inclusion_tag('components/ui/badge.html')
def skote_badge(text, type='primary', rounded=False, soft=False):
    """
    Render a badge component

    Args:
        text: Badge text
        type: Badge color (primary, secondary, success, danger, warning, info, light, dark)
        rounded: Use rounded pill style
        soft: Use soft/lighter background

    Usage:
        {% skote_badge "New" type="success" rounded=True %}
    """
    return {
        'text': text,
        'type': type,
        'rounded': rounded,
        'soft': soft,
    }


@register.inclusion_tag('components/ui/button.html')
def skote_button(text, type='primary', size='', outline=False, block=False,
                 disabled=False, href=None, icon=None, icon_position='left'):
    """
    Render a button component

    Args:
        text: Button text
        type: Button color (primary, secondary, success, danger, warning, info, light, dark)
        size: Button size (sm, lg, or empty for default)
        outline: Use outline style
        block: Full width button
        disabled: Disabled state
        href: If provided, renders as link instead of button
        icon: Icon class (e.g., 'bx bx-check')
        icon_position: Position of icon ('left' or 'right')

    Usage:
        {% skote_button "Submit" type="primary" icon="bx bx-check" %}
        {% skote_button "Delete" type="danger" outline=True %}
    """
    return {
        'text': text,
        'type': type,
        'size': size,
        'outline': outline,
        'block': block,
        'disabled': disabled,
        'href': href,
        'icon': icon,
        'icon_position': icon_position,
    }


@register.inclusion_tag('components/ui/modal.html')
def skote_modal(modal_id, title, body=None, size='', centered=False,
                scrollable=False, footer_buttons=None):
    """
    Render a modal component

    Args:
        modal_id: Unique ID for the modal
        title: Modal title
        body: Modal body content
        size: Modal size (sm, lg, xl, or empty for default)
        centered: Vertically center the modal
        scrollable: Enable scrolling for long content
        footer_buttons: List of button configs for footer

    Usage:
        {% skote_modal "myModal" "Modal Title" body="Modal content" %}
    """
    return {
        'modal_id': modal_id,
        'title': title,
        'body': mark_safe(body) if body else None,
        'size': size,
        'centered': centered,
        'scrollable': scrollable,
        'footer_buttons': footer_buttons or [],
    }


@register.inclusion_tag('components/ui/breadcrumb.html')
def skote_breadcrumb(items):
    """
    Render a breadcrumb component

    Args:
        items: List of dicts with 'text' and optional 'url' keys

    Usage:
        {% skote_breadcrumb items %}
        where items = [
            {'text': 'Home', 'url': '/'},
            {'text': 'Products', 'url': '/products/'},
            {'text': 'Detail'}  # Last item is active
        ]
    """
    return {
        'items': items,
    }


@register.inclusion_tag('components/ui/progress_bar.html')
def skote_progress(value, max_value=100, type='primary', striped=False,
                   animated=False, label=None, height=None):
    """
    Render a progress bar component

    Args:
        value: Current progress value
        max_value: Maximum value (default 100)
        type: Color type (primary, secondary, success, danger, warning, info)
        striped: Show striped pattern
        animated: Animate stripes
        label: Optional label text
        height: Optional custom height (e.g., '20px')

    Usage:
        {% skote_progress 75 type="success" striped=True %}
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    return {
        'value': value,
        'max_value': max_value,
        'percentage': percentage,
        'type': type,
        'striped': striped,
        'animated': animated,
        'label': label,
        'height': height,
    }


@register.simple_tag
def skote_icon(icon_class, size=None, color=None):
    """
    Render an icon

    Args:
        icon_class: Icon class (e.g., 'bx bx-home', 'mdi mdi-account')
        size: Font size (e.g., '24px', '2rem')
        color: Color class or hex value

    Usage:
        {% skote_icon 'bx bx-home' size='24px' %}
    """
    style_parts = []
    if size:
        style_parts.append(f'font-size: {size}')
    if color:
        if color.startswith('#') or color.startswith('rgb'):
            style_parts.append(f'color: {color}')
        else:
            icon_class += f' text-{color}'

    style = f' style="{"; ".join(style_parts)}"' if style_parts else ''
    return mark_safe(f'<i class="{icon_class}"{style}></i>')


@register.inclusion_tag('components/ui/carousel.html')
def skote_carousel(carousel_id, slides, controls=True, indicators=True,
                   interval=3000, fade=False, captions=False):
    """
    Render a carousel component

    Args:
        carousel_id: Unique ID for the carousel
        slides: List of dicts with 'image', optional 'caption', 'description'
        controls: Show prev/next controls
        indicators: Show slide indicators
        interval: Auto-slide interval in ms (0 to disable)
        fade: Use fade transition instead of slide
        captions: Show captions overlay

    Usage:
        {% skote_carousel "myCarousel" slides controls=True %}
        where slides = [
            {'image': '/static/img1.jpg', 'caption': 'Title', 'description': 'Text'},
            {'image': '/static/img2.jpg'},
        ]
    """
    return {
        'carousel_id': carousel_id,
        'slides': slides,
        'controls': controls,
        'indicators': indicators,
        'interval': interval,
        'fade': fade,
        'captions': captions,
    }


@register.inclusion_tag('components/ui/dropdown.html')
def skote_dropdown(button_text, items, dropdown_id=None, button_type='primary',
                   button_size='', split=False, direction='down', alignment='start'):
    """
    Render a dropdown component

    Args:
        button_text: Dropdown button text
        items: List of dicts with 'text', 'url', optional 'divider', 'header'
        dropdown_id: Unique ID (auto-generated if not provided)
        button_type: Button color
        button_size: Button size (sm, lg)
        split: Use split button style
        direction: Direction (down, up, start, end)
        alignment: Menu alignment (start, end)

    Usage:
        {% skote_dropdown "Actions" items %}
        where items = [
            {'text': 'Edit', 'url': '/edit/'},
            {'divider': True},
            {'text': 'Delete', 'url': '/delete/'},
        ]
    """
    import uuid
    if not dropdown_id:
        dropdown_id = f'dropdown_{uuid.uuid4().hex[:8]}'

    return {
        'button_text': button_text,
        'items': items,
        'dropdown_id': dropdown_id,
        'button_type': button_type,
        'button_size': button_size,
        'split': split,
        'direction': direction,
        'alignment': alignment,
    }


@register.inclusion_tag('components/ui/offcanvas.html')
def skote_offcanvas(offcanvas_id, title, body=None, placement='start',
                    backdrop=True, scroll=False):
    """
    Render an offcanvas component

    Args:
        offcanvas_id: Unique ID for the offcanvas
        title: Offcanvas title
        body: Body content (HTML safe)
        placement: Position (start, end, top, bottom)
        backdrop: Show backdrop
        scroll: Allow body scrolling

    Usage:
        {% skote_offcanvas "menu" "Navigation" body=content placement="start" %}
    """
    return {
        'offcanvas_id': offcanvas_id,
        'title': title,
        'body': mark_safe(body) if body else None,
        'placement': placement,
        'backdrop': backdrop,
        'scroll': scroll,
    }


@register.inclusion_tag('components/ui/placeholder.html')
def skote_placeholder(width='100%', height='auto', lines=3, animation='glow',
                     size='', color=''):
    """
    Render a placeholder/skeleton loader

    Args:
        width: Placeholder width
        height: Placeholder height
        lines: Number of lines for text placeholder
        animation: Animation type (glow, wave)
        size: Size variant (xs, sm, lg)
        color: Background color class

    Usage:
        {% skote_placeholder lines=3 animation="wave" %}
    """
    return {
        'width': width,
        'height': height,
        'lines': lines,
        'animation': animation,
        'size': size,
        'color': color,
    }


@register.inclusion_tag('components/ui/toast.html')
def skote_toast(toast_id, title, message, type='info', icon=None,
               autohide=True, delay=5000, position='top-right'):
    """
    Render a toast notification

    Args:
        toast_id: Unique ID for the toast
        title: Toast title
        message: Toast message
        type: Toast color type
        icon: Icon class
        autohide: Auto hide after delay
        delay: Delay in ms before hiding
        position: Toast position (top-right, top-left, bottom-right, bottom-left)

    Usage:
        {% skote_toast "toast1" "Success" "Item saved!" type="success" %}
    """
    return {
        'toast_id': toast_id,
        'title': title,
        'message': message,
        'type': type,
        'icon': icon,
        'autohide': autohide,
        'delay': delay,
        'position': position,
    }


@register.inclusion_tag('components/ui/tabs.html')
def skote_tabs(tabs, tab_id=None, justified=False, pills=False, vertical=False):
    """
    Render tabs component

    Args:
        tabs: List of dicts with 'title', 'content', optional 'active', 'icon'
        tab_id: Unique ID for tab group
        justified: Full width tabs
        pills: Pill style tabs
        vertical: Vertical tabs

    Usage:
        {% skote_tabs tabs %}
        where tabs = [
            {'title': 'Tab 1', 'content': '<p>Content 1</p>', 'active': True},
            {'title': 'Tab 2', 'content': '<p>Content 2</p>'},
        ]
    """
    import uuid
    if not tab_id:
        tab_id = f'tab_{uuid.uuid4().hex[:8]}'

    return {
        'tabs': tabs,
        'tab_id': tab_id,
        'justified': justified,
        'pills': pills,
        'vertical': vertical,
    }


@register.inclusion_tag('components/ui/accordion.html')
def skote_accordion(items, accordion_id=None, flush=False, always_open=False):
    """
    Render an accordion component

    Args:
        items: List of dicts with 'title', 'content', optional 'active'
        accordion_id: Unique ID for accordion
        flush: Flush style (no borders)
        always_open: Allow multiple items open

    Usage:
        {% skote_accordion items %}
        where items = [
            {'title': 'Item 1', 'content': '<p>Content</p>', 'active': True},
            {'title': 'Item 2', 'content': '<p>Content</p>'},
        ]
    """
    import uuid
    if not accordion_id:
        accordion_id = f'accordion_{uuid.uuid4().hex[:8]}'

    return {
        'items': items,
        'accordion_id': accordion_id,
        'flush': flush,
        'always_open': always_open,
    }


@register.simple_tag
def skote_rating(rating, max_rating=5, size='md', color='warning', readonly=True):
    """
    Render a star rating component

    Args:
        rating: Current rating value
        max_rating: Maximum rating (default 5)
        size: Icon size (sm, md, lg)
        color: Star color
        readonly: Display only (not interactive)

    Usage:
        {% skote_rating 4.5 %}
    """
    size_map = {'sm': '16px', 'md': '20px', 'lg': '24px'}
    icon_size = size_map.get(size, '20px')

    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = max_rating - full_stars - (1 if has_half else 0)

    html = '<div class="rating">'

    # Full stars
    for _ in range(full_stars):
        html += f'<i class="bx bxs-star text-{color}" style="font-size: {icon_size}"></i>'

    # Half star
    if has_half:
        html += f'<i class="bx bxs-star-half text-{color}" style="font-size: {icon_size}"></i>'

    # Empty stars
    for _ in range(empty_stars):
        html += f'<i class="bx bx-star text-{color}" style="font-size: {icon_size}"></i>'

    html += '</div>'
    return mark_safe(html)


@register.simple_tag
def skote_spinner(type='border', size='', color='primary'):
    """
    Render a loading spinner

    Args:
        type: Spinner type (border, grow)
        size: Size (sm, or empty for default)
        color: Color variant

    Usage:
        {% skote_spinner type="border" color="primary" %}
    """
    spinner_class = f'spinner-{type}'
    if size:
        spinner_class += f' spinner-{type}-{size}'

    return mark_safe(
        f'<div class="{spinner_class} text-{color}" role="status">'
        f'<span class="visually-hidden">Loading...</span></div>'
    )


@register.simple_tag
def skote_avatar(name='', image=None, size='md', status=None, rounded=True):
    """
    Render an avatar component

    Args:
        name: Name for initials if no image
        image: Image URL
        size: Size (xs, sm, md, lg, xl)
        status: Status indicator (online, offline, away)
        rounded: Circular avatar

    Usage:
        {% skote_avatar name="John Doe" size="lg" status="online" %}
        {% skote_avatar image="/path/to/img.jpg" size="md" %}
    """
    size_map = {
        'xs': 'avatar-xs',
        'sm': 'avatar-sm',
        'md': 'avatar-md',
        'lg': 'avatar-lg',
        'xl': 'avatar-xl',
    }
    avatar_class = size_map.get(size, 'avatar-md')

    if image:
        html = f'<div class="{avatar_class} {"rounded-circle" if rounded else ""}">'
        html += f'<img src="{image}" alt="{name}" class="{'rounded-circle ' if rounded else ''}img-thumbnail">'
    else:
        initials = ''.join([n[0].upper() for n in name.split()[:2]]) if name else '?'
        html = f'<div class="{avatar_class}">'
        html += f'<span class="avatar-title {"rounded-circle" if rounded else ""} bg-primary">{initials}</span>'

    if status:
        status_colors = {
            'online': 'success',
            'offline': 'secondary',
            'away': 'warning',
            'busy': 'danger',
        }
        color = status_colors.get(status, 'secondary')
        html += f'<span class="avatar-status-indicator bg-{color}"></span>'

    html += '</div>'
    return mark_safe(html)


# TABLE COMPONENTS

@register.inclusion_tag('components/tables/basic_table.html')
def skote_table(headers, rows, table_class='', striped=False, bordered=False,
                hover=False, small=False, responsive=True):
    """
    Render a basic table

    Args:
        headers: List of column headers
        rows: List of lists containing row data
        table_class: Additional CSS classes
        striped: Striped rows
        bordered: Bordered table
        hover: Hover effect on rows
        small: Compact table
        responsive: Wrap in responsive container

    Usage:
        {% skote_table headers rows striped=True hover=True %}
        where headers = ['Name', 'Email', 'Role']
        and rows = [['John', 'john@email.com', 'Admin'], ...]
    """
    return {
        'headers': headers,
        'rows': rows,
        'table_class': table_class,
        'striped': striped,
        'bordered': bordered,
        'hover': hover,
        'small': small,
        'responsive': responsive,
    }


@register.inclusion_tag('components/tables/datatable.html')
def skote_datatable(table_id, headers, data_url=None, columns=None,
                   ordering=True, searching=True, paging=True,
                   page_length=10, dom='lfrtip'):
    """
    Render a DataTable with AJAX support

    Args:
        table_id: Unique table ID
        headers: List of column headers
        data_url: AJAX URL for data (optional, use static data if None)
        columns: List of column configs for DataTables
        ordering: Enable column sorting
        searching: Enable search box
        paging: Enable pagination
        page_length: Rows per page
        dom: DataTables DOM positioning

    Usage:
        {% skote_datatable "myTable" headers data_url="/api/data/" %}
    """
    import uuid
    if not table_id:
        table_id = f'datatable_{uuid.uuid4().hex[:8]}'

    return {
        'table_id': table_id,
        'headers': headers,
        'data_url': data_url,
        'columns': columns or [],
        'ordering': ordering,
        'searching': searching,
        'paging': paging,
        'page_length': page_length,
        'dom': dom,
    }


@register.simple_tag
def skote_table_actions(edit_url=None, delete_url=None, view_url=None, custom_actions=None):
    """
    Render table action buttons

    Args:
        edit_url: Edit URL
        delete_url: Delete URL
        view_url: View URL
        custom_actions: List of dicts with 'url', 'icon', 'class', 'text'

    Usage:
        {% skote_table_actions edit_url="/edit/1/" delete_url="/delete/1/" %}
    """
    html = '<div class="btn-group" role="group">'

    if view_url:
        html += f'<a href="{view_url}" class="btn btn-sm btn-outline-info" title="View"><i class="bx bx-show"></i></a>'

    if edit_url:
        html += f'<a href="{edit_url}" class="btn btn-sm btn-outline-primary" title="Edit"><i class="bx bx-edit"></i></a>'

    if delete_url:
        html += f'<a href="{delete_url}" class="btn btn-sm btn-outline-danger" title="Delete" onclick="return confirm(\'Are you sure?\')"><i class="bx bx-trash"></i></a>'

    if custom_actions:
        for action in custom_actions:
            url = action.get('url', '#')
            icon = action.get('icon', '')
            btn_class = action.get('class', 'btn-outline-secondary')
            text = action.get('text', '')
            html += f'<a href="{url}" class="btn btn-sm {btn_class}" title="{text}"><i class="{icon}"></i></a>'

    html += '</div>'
    return mark_safe(html)
