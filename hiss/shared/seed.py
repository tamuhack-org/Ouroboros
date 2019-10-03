# Seed File
# python manage.py shell < shared/seed.py
from user.models import User
from application.models import Application
import random
import datetime
import pytz

common_names = [
    "Noah",
    "Liam",
    "Mason",
    "Jacob",
    "William",
    "Ethan",
    "Michael",
    "Alexander",
    "James",
    "Daniel",
    "Emma",
    "Olivia",
    "Sophia",
    "Ava",
    "Isabella",
    "Mia",
    "Abigail",
    "Emily",
    "Charlotte",
    "Harper",
]


def seed_database(num_of_users: int, num_of_active: int, num_of_applications: int):
    """
    Function that creates Users and Applications to make testing easier.
    To run use -- python manage.py shell < shared/seed.py
    WARNING - Will delete most of the Users and Applications when run.
    DO not use in production
    """
    if not num_of_users >= num_of_active >= num_of_applications:
        return
    print("Starting the seeding process")
    arr = []
    # Clear existing objects
    User.objects.all().filter(is_superuser=False).delete()
    Application.objects.all().filter(last_name="Seedoe").delete()
    for i in range(num_of_users):
        # Generate fake name, email, is_active status, and if they should make an app
        random_name = random.choice(common_names)
        fake_email = random_name + str(i) + "@seed.com"
        fake_is_active = False
        create_an_app = False
        if i < num_of_active:
            fake_is_active = True
        if i < num_of_applications:
            create_an_app = True

        arr.append(
            {
                "email": fake_email,
                "password": "a",  # This is the password for login
                "is_active": fake_is_active,
                "make_app": create_an_app,
                "name": random_name,
            }
        )
    random.shuffle(arr)
    # Create the users
    for e in arr:
        print("Creating User ...", e["email"])
        user = User.objects.create(email=e["email"], is_active=e["is_active"])
        user.set_password(e["password"])
        user.save()
    # Create the Applications
    for e in arr:
        current_user = User.objects.get(email=e["email"])
        if e["make_app"]:
            # FUTURE -> Might want to change fake_date_range or remove it.
            fake_date_range = datetime.datetime(
                2019, 9, random.randint(1, 30), 22, 30, 52, 32320, tzinfo=pytz.UTC
            )
            current_app = Application.objects.create(
                first_name=e["name"],
                last_name="Seedoe",
                notes=e["email"],
                major="Computer Science",
                gender=random.choice(["M", "M", "M", "F"]),
                race=[
                    random.choice(
                        [
                            "Asian",
                            "Black",
                            "Hispanic",
                            "Native Hawaiian",
                            "White",
                            "NA",
                            "Other",
                        ]
                    )
                ],
                classification=random.choice(
                    ["Fr", "Fr", "Fr", "Fr", "So", "Jr", "Sr", "Ot"]
                ),
                grad_term=random.choice(
                    [
                        "Fall 2019",
                        "Spring 2020",
                        "Fall 2020",
                        "Spring 2021",
                        "Fall 2021",
                        "Spring 2022",
                        "Fall 2022",
                        "Spring 2023",
                    ]
                ),
                num_hackathons_attended=random.choice(
                    ["0", "0", "0", "1-3", "1-3", "4-7", "8-10", "10+"]
                ),
                previous_attendant=random.choice(
                    [True, True, True, True, True, True, True, True, False]
                ),
                tamu_student=True,
                extra_links="extra_links",
                question1="question1",
                question2="question2",
                question3="question3",
                approved=random.choice(
                    [
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        True,
                        True,
                        True,
                        False,
                    ]
                ),
                agree_to_coc=True,
                is_adult=True,
                additional_accommodations="f",
                # Some random UID
                resume="150650bf-3967-42ca-aa21-1ba067af2df5.pdf",
                wave_id=1,
                user_id=current_user.id,
                user_email=current_user.email,
            )
            # FUTURE -> Remove this line to have datetime_submitted be realtime
            current_app.datetime_submitted = fake_date_range
            current_app.save()
            print(
                "Created app",
                current_app,
                current_user.email,
                current_app.datetime_submitted,
                datetime.datetime(
                    2019, 9, random.randint(1, 30), 22, 30, 52, 32320, tzinfo=pytz.UTC
                ),
            )


# num_of_users >= num_of_active >= num_of_applications
# seed_database(100, 85, 75)
seed_database(50, 40, 30)
