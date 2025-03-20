from application.models import (
    GENDERS, MALE, FEMALE,
    STATUS_CONFIRMED, STATUS_ADMITTED, STATUS_CHECKED_IN,STATUS_REJECTED,
    Application
    )

def dashboard_callback(request, context):
    '''
    This callback is called within the templates/admin/index.html file
    This function queries application data within the database and is configured in hiss/settings/base.py as the default callback file
    Callbacks are used to get data in python and send it over to the django template to be queried whenever the admin dashboard loads
    '''
    context['total_confirmed'] = Application.objects.filter(status=STATUS_CONFIRMED).count()
    context['total_admitted'] = Application.objects.filter(status=STATUS_ADMITTED).count()
    context['total_checked'] = Application.objects.filter(status=STATUS_CHECKED_IN).count()
    context['total_rejected'] = Application.objects.filter(status=STATUS_REJECTED).count()

    context['gender_male'] = Application.objects.filter(gender=MALE).count()
    context['gender_female'] = Application.objects.filter(gender=FEMALE).count()


    return context