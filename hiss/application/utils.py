from application.models import (
    STATUS_CONFIRMED, STATUS_ADMITTED, STATUS_CHECKED_IN, STATUS_EXPIRED,
    Application
    )

def dashboard_callback(request, context):
    '''
    This callback is called within the templates/admin/index.html file
    This function queries application data within the database and is configured in 
    hiss/settings/base.py as the default callback file. Callbacks are used to get 
    data in python and send it over to hiss/templates/admin/index.html template to
    be queried whenever the admin dashboard loads
    '''
    context['total_confirmed'] = Application.objects.filter(status=STATUS_CONFIRMED).count()
    context['total_application'] = Application.objects.count()
    context['total_checked'] = Application.objects.filter(status=STATUS_CHECKED_IN).count()
    context['total_admitted'] = Application.objects.filter(status=STATUS_ADMITTED).count()
    context['total_hardware'] = Application.objects.filter(wares="H").count()
    context['total_waitlisted'] = Application.objects.filter(status=STATUS_EXPIRED).count()

    return context