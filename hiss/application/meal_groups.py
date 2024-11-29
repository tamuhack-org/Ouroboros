from django.db import transaction
from models import Application

NUM_GROUPS = 4
RESTRICTED_FRONTLOAD_FACTOR = 1.3

def assign_food_groups():
    veg_apps = []
    nobeef_apps = []
    nopork_apps = []
    allergy_apps = []
    othernonveg_apps = []
    
    applicants = Application.objects.filter(status__in=['A', 'E', 'C'])

    for app in applicants:
        if "Vegetarian" in app.dietary_restrictions or "Vegan" in app.dietary_restrictions:
            veg_apps.append(app)
        elif "No-Beef" in app.dietary_restrictions:
            nobeef_apps.append(app)
        elif "No-Pork" in app.dietary_restrictions:
            nopork_apps.append(app)
        elif "Food-Allergy" in app.dietary_restrictions:
            allergy_apps.append(app)
        else:
            othernonveg_apps.append(app)

    restricted_apps = veg_apps + nobeef_apps + nopork_apps + allergy_apps
    num_apps = len(restricted_apps) + len(othernonveg_apps)

    group_size = num_apps // NUM_GROUPS
    restricted_percent = len(restricted_apps) / num_apps
    restricted_target = restricted_percent * RESTRICTED_FRONTLOAD_FACTOR
    restricted_per_group = restricted_target * group_size

    groups = [[] for _ in range(NUM_GROUPS)]
    group_restricted_count = [0] * NUM_GROUPS

    # Assign restricted applicants
    for i in range(NUM_GROUPS):
        groups[i] = restricted_apps[:int(restricted_per_group)]
        restricted_apps = restricted_apps[int(restricted_per_group):]
        group_restricted_count[i] = len(groups[i])

    # Assign unrestricted applicants
    for i in range(NUM_GROUPS):
        groups[i] += othernonveg_apps[:group_size - group_restricted_count[i]]
        othernonveg_apps = othernonveg_apps[group_size - group_restricted_count[i]:]
    groups[-1] += othernonveg_apps

    # Update database with meal groups
    with transaction.atomic():
        for i, group in enumerate(groups):
            group_letter = chr(65 + i)
            for app in group:
                app.meal_group = group_letter
                app.save()

    return {f"Group {chr(65 + i)}": len(group) for i, group in enumerate(groups)}
