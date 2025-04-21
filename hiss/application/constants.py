from __future__ import annotations

from django.conf import settings
from django.utils import timezone

PYTHON = "Python"
JAVA_SCRIPT = "JavaScript"
TYPE_SCRIPT = "TypeScript"
JAVA = "Java"
C_SHARP = "C#"
C_LANG = "C"
CPP = "C++"
GOLANG = "Go"
R_LANG = "R"
SWIFT = "Swift"
DART = "Dart"
KOTLIN = "Kotlin"
RUBY = "Ruby"
RUST = "Rust"
SCALA = "Scala"
SQL = "SQL"
HTML = "HTML"
CSS = "CSS"
PHP = "PHP"
ELIXIR = "Elixir"
VERILOG = "Verilog"
HASKELL = "Haskell"
LUA = "Lua"
# Concepts
MACHINE_LEARNING = "ML"
FULL_STACK = "full-stack"
FRONT_END = "front-end"
BACK_END = "back-end"
WEB = "web-dev"
MOBILE = "mobile-dev"
DESIGN = "design"
DATA_SCIENCE = "data-science"
DEV_OPS = "dev-ops"
CLOUD = "cloud"
DATABASES = "databases"
UI_UX = "UI/UX"
GENERATIVE_AI = "generative-ai"
DATA_VIS = "data-visualization"
COMPUTER_GRAPHICS = "computer-graphics"
GAME_DEV = "game-development"
CYBERSECURITY = "cybersecurity"
DATA_STRUCTURES = "data-structures"
REST_APIS = "rest-apis"
TESTING = "software-testing"
MICROCONTROLLERS = "microcontrollers"
SYSTEMS_PROGRAMMING = "computer-systems-programming"
HARDWARE = "computer-hardware"
OS = "operating-systems"
# Industry Standards
AWS = "AWS"
GOOGLE_CLOUD = "Google-Cloud"
MS_AZURE = "Microsoft-Azure"
VERCEL = "Vercel"
POSTGRESQL = "PostgreSQL"
MONGO_DB = "MongoDB"
REACT = "React"
ANGULAR = "Angular"
VUE = "Vue.js"
SVELTE = "Svelte"
BOOTSTRAP = "Bootstrap"
RAILS = "Ruby-on-Rails"
DJANGO = "Django"
FIREBASE = "Firebase"
GIT = "Git"
UNIX_LINUX = "Unix/Linux"
JUPYTER_NOTEBOOKS = "Jupyter-Notebooks"
NODE_JS = "Node.js"
DOCKER = "Docker"
KUBERNETES = "Kubernetes"
TENSORFLOW = "Tensorflow"
PYTORCH = "PyTorch"
FLUTTER = "Flutter"
REACT_NATIVE = "React-Native"

TECHNOLOGY_EXPERIENCE = (
    (PYTHON, "Python"),
    (JAVA_SCRIPT, "JavaScript"),
    (TYPE_SCRIPT, "TypeScript"),
    (JAVA, "Java"),
    (C_SHARP, "C#"),
    (C_LANG, "C"),
    (CPP, "C++"),
    (GOLANG, "Golang"),
    (R_LANG, "R"),
    (SWIFT, "Swift"),
    (DART, "Dart"),
    (KOTLIN, "Kotlin"),
    (RUBY, "Ruby"),
    (RUST, "Rust"),
    (SCALA, "Scala"),
    (SQL, "SQL"),
    (HTML, "HTML"),
    (CSS, "CSS"),
    (PHP, "PHP"),
    (ELIXIR, "Elixir"),
    (VERILOG, "Verilog"),
    (HASKELL, "Haskell"),
    (LUA, "Lua"),
    (FULL_STACK, "Full Stack"),
    (FRONT_END, "Front End"),
    (BACK_END, "Back End"),
    (WEB, "Web"),
    (MOBILE, "Mobile"),
    (DESIGN, "Design"),
    (DEV_OPS, "Dev Ops"),
    (CLOUD, "Cloud"),
    (DATA_SCIENCE, "Data Science"),
    (MACHINE_LEARNING, "Machine Learning"),
    (DATABASES, "Databases"),
    (UI_UX, "UI/UX"),
    (GENERATIVE_AI, "Generative AI"),
    (DATA_VIS, "Data Visualization"),
    (COMPUTER_GRAPHICS, "Computer Graphics"),
    (GAME_DEV, "Game Development"),
    (CYBERSECURITY, "Cybersecurity"),
    (DATA_STRUCTURES, "Data Structures"),
    (REST_APIS, "REST APIs"),
    (TESTING, "Software Testing"),
    (MICROCONTROLLERS, "Microcontrollers"),
    (SYSTEMS_PROGRAMMING, "Computer Systems Programming"),
    (HARDWARE, "Computer Hardware"),
    (OS, "Operating Systems"),
    (AWS, "AWS"),
    (GOOGLE_CLOUD, "Google Cloud"),
    (MS_AZURE, "Microsoft Azure"),
    (VERCEL, "Vercel"),
    (POSTGRESQL, "PostgreSQL"),
    (MONGO_DB, "MongoDB"),
    (REACT, "React"),
    (ANGULAR, "Angular"),
    (VUE, "Vue.js"),
    (SVELTE, "Svelte"),
    (BOOTSTRAP, "Bootstrap"),
    (RAILS, "Ruby on Rails"),
    (DJANGO, "Django"),
    (FIREBASE, "Firebase"),
    (GIT, "Git"),
    (UNIX_LINUX, "Unix/Linux"),
    (JUPYTER_NOTEBOOKS, "Jupyter Notebooks"),
    (NODE_JS, "Node.js"),
    (DOCKER, "Docker"),
    (KUBERNETES, "Kubernetes"),
    (TENSORFLOW, "Tensorflow"),
    (PYTORCH, "PyTorch"),
    (FLUTTER, "Flutter"),
    (REACT_NATIVE, "React Native"),
)

VEGAN = "Vegan"
VEGETARIAN = "Vegetarian"
NO_BEEF = "No-Beef"
NO_PORK = "No-Pork"
HALAL = "Halal"
KOSHER = "Kosher"
GLUTEN_FREE = "Gluten-Free"
FOOD_ALLERGY = "Food-Allergy"
OTHER_DIETARY_RESTRICTION = "Other"

DIETARY_RESTRICTIONS = (
    (VEGAN, "Vegan"),
    (VEGETARIAN, "Vegetarian"),
    (NO_BEEF, "No Beef"),
    (NO_PORK, "No Pork"),
    (HALAL, "Halal"),
    (KOSHER, "Kosher"),
    (GLUTEN_FREE, "Gluten-Free"),
    (FOOD_ALLERGY, "Food Allergy"),
    (OTHER_DIETARY_RESTRICTION, "Other"),
)
MAX_AGE = 18
AGREE = ((True, "Agree"),)
AGREE_DISAGREE = ((True, "Agree"), (False, "Disagree"))
TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))
NO_ANSWER = "NA"
MALE = "M"
FEMALE = "F"
NON_BINARY = "NB"
GENDER_OTHER = "X"
GENDERS: list[tuple[str, str]] = [
    (NO_ANSWER, "Prefer not to answer"),
    (MALE, "Male"),
    (FEMALE, "Female"),
    (NON_BINARY, "Non-binary"),
    (GENDER_OTHER, "Prefer to self-describe"),
]
AMERICAN_INDIAN = "AI"
ASIAN_INDIAN_SUB = "ASI"
ASIAN_EAST = "ASE"
ASIAN_SOUTHEAST = "ASSE"
ASIAN_OTHER = "AS"
BLACK = "BL"
HISPANIC = "HI"
NATIVE_HAWAIIAN = "NH"
MIDDLE_EASTERN_NORTH_AFRICAN = "MENA"
WHITE = "WH"
RACE_OTHER = "O"
RACES: list[tuple[str, str]] = [
    (AMERICAN_INDIAN, "American Indian or Alaskan Native"),
    (ASIAN_INDIAN_SUB, "Asian (Indian Subcontinent)"),
    (ASIAN_EAST, "Asian (East Asia)"),
    (ASIAN_SOUTHEAST, "Asian (Southeast Asia)"),
    (ASIAN_OTHER, "Asian (Other)"),
    (BLACK, "Black or African-American"),
    (HISPANIC, "Hispanic or Latino"),
    (NATIVE_HAWAIIAN, "Native Hawaiian or other Pacific Islander"),
    (MIDDLE_EASTERN_NORTH_AFRICAN, "Middle Eastern or North African"),
    (WHITE, "White"),
    (NO_ANSWER, "Prefer not to answer"),
    (RACE_OTHER, "Prefer to self-describe"),
]
FRESHMAN = "Fr"
SOPHOMORE = "So"
JUNIOR = "Jr"
SENIOR = "Sr"
MASTERS = "Ma"
PHD = "PhD"
CLASSIFICATION_OTHER = "O"
CLASSIFICATIONS: list[tuple[str, str]] = [
    (FRESHMAN, "Freshman"),
    (SOPHOMORE, "Sophomore"),
    (JUNIOR, "Junior"),
    (SENIOR, "Senior"),
    (MASTERS, "Master's Student"),
    (PHD, "PhD Student"),
    (CLASSIFICATION_OTHER, "Other"),
]
HACKATHONS_0 = "0"
HACKATHONS_1 = "1"
HACKATHONS_2_TO_3 = "2-3"
HACKATHONS_4_TO_5 = "4-5"
HACKATHONS_6 = "6+"
HACKATHON_TIMES: list[tuple[str, str]] = [
    (HACKATHONS_0, "This will be my first!"),
    (HACKATHONS_1, "1"),
    (HACKATHONS_2_TO_3, "2-3"),
    (HACKATHONS_4_TO_5, "4-5"),
    (HACKATHONS_6, "6+"),
]
STUDY_LESS_THAN_SECONDARY = "Less than Secondary / High School"
STUDY_SECONDARY = "Secondary / High School"
STUDY_UNDERGRAD_2YEAR = (
    "Undergraduate University (2 year - community college or similar)"
)
STUDY_UNDERGRAD_3YEAR = "Undergraduate University (3+ year)"
STUDY_GRADUATE = "Graduate University (Masters, Professional, Doctoral, etc)"
STUDY_CODE_SCHOOL = "Code School / Bootcamp"
STUDY_OTHER_VOCATIONAL = "Other Vocational / Trade Program or Apprenticeship"
STUDY_POSTDOC = "Post Doctorate"
STUDY_OTHER = "Other"
STUDY_NOT_STUDENT = "I'm not currently a student"
STUDY_NO_ANSWER = "Prefer not to answer"
LEVELS_OF_STUDY = [
    (STUDY_LESS_THAN_SECONDARY, STUDY_LESS_THAN_SECONDARY),
    (STUDY_SECONDARY, STUDY_SECONDARY),
    (STUDY_UNDERGRAD_2YEAR, STUDY_UNDERGRAD_2YEAR),
    (STUDY_UNDERGRAD_3YEAR, STUDY_UNDERGRAD_3YEAR),
    (STUDY_GRADUATE, STUDY_GRADUATE),
    (STUDY_CODE_SCHOOL, STUDY_CODE_SCHOOL),
    (STUDY_OTHER_VOCATIONAL, STUDY_OTHER_VOCATIONAL),
    (STUDY_POSTDOC, STUDY_POSTDOC),
    (STUDY_OTHER, STUDY_OTHER),
    (STUDY_NOT_STUDENT, STUDY_NOT_STUDENT),
    (STUDY_NO_ANSWER, STUDY_NO_ANSWER),
]
GRAD_YEARS: list[tuple[int, int]] = [
    (int(y), int(y))
    for y in range(
        timezone.now().year, timezone.now().year + settings.MAX_YEARS_ADMISSION
    )
]
DRIVING = "D"
EVENT_PROVIDED_BUS = "B"
EVENT_PROVIDED_BUS_UT = "BUT"
EVENT_PROVIDED_BUS_UTD = "BUTD"
EVENT_PROVIDED_BUS_UTA = "BUTA"
EVENT_PROVIDED_BUS_UTSA = "BUTSA"
EVENT_PROVIDED_BUS_UTRGV = "BUTRGV"
OTHER_BUS = "OB"
FLYING = "F"
PUBLIC_TRANSPORTATION = "P"
MANUAL_POWER = "M"
TRANSPORT_MODES: list[tuple[str, str]] = [
    (DRIVING, "Driving"),
    (EVENT_PROVIDED_BUS, f"{settings.EVENT_NAME} Bus"),
    (EVENT_PROVIDED_BUS_UT, f"{settings.EVENT_NAME} Bus - UT Austin"),
    (EVENT_PROVIDED_BUS_UTD, f"{settings.EVENT_NAME} Bus - UT Dallas"),
    (EVENT_PROVIDED_BUS_UTA, f"{settings.EVENT_NAME} Bus - UT Arlington"),
    (EVENT_PROVIDED_BUS_UTSA, f"{settings.EVENT_NAME} Bus - UTSA"),
    (EVENT_PROVIDED_BUS_UTRGV, f"{settings.EVENT_NAME} Bus - UTRGV"),
    (OTHER_BUS, "Other Bus (Greyhound, Megabus, etc.)"),
    (FLYING, "Flying"),
    (PUBLIC_TRANSPORTATION, "Public Transportation"),
    (MANUAL_POWER, "Walking/Biking"),
]
QUESTION1_TEXT = "Tell us your best programming joke."
UNISEX_XXS = "XXS"
UNISEX_XS = "XS"
UNISEX_S = "S"
UNISEX_M = "M"
UNISEX_L = "L"
UNISEX_XL = "XL"
UNISEX_XXL = "XXL"
SHIRT_SIZES = [
    (UNISEX_XXS, "XXS"),
    (UNISEX_XS, "XS"),
    (UNISEX_S, "S"),
    (UNISEX_M, "M"),
    (UNISEX_L, "L"),
    (UNISEX_XL, "XL"),
    (UNISEX_XXL, "XXL"),
]
STATUS_PENDING = "P"
STATUS_REJECTED = "R"
STATUS_ADMITTED = "A"
STATUS_CONFIRMED = "C"
STATUS_DECLINED = "X"
STATUS_CHECKED_IN = "I"
STATUS_EXPIRED = "E"
STATUS_OPTIONS = [
    (STATUS_PENDING, "Under Review"),
    (STATUS_REJECTED, "Rejected"),
    (STATUS_ADMITTED, "Admitted"),
    (STATUS_CONFIRMED, "Confirmed"),
    (STATUS_DECLINED, "Declined"),
    (STATUS_CHECKED_IN, "Checked in"),
    (STATUS_EXPIRED, "Waitlisted (Expired, internally)"),
]
HAS_TEAM = "HT"
HAS_NO_TEAM = "HNT"
HAS_TEAM_OPTIONS = [
    (HAS_TEAM, "I do have a team"),
    (HAS_NO_TEAM, "I do not have a team"),
]
CS = "Computer Science"
CE = "Computer Engineering"
COMP = "Computing"
EE = "Electrical Engineering"
MIS = "Management Information Systems"
DS = "Data Science/Engineering"
GENE = "General Engineering"
BMEN = "Biomedical Engineering"
CHEM = "Chemical Engineering"
CIVIL = "Civil Engineering"
INDU = "Industrial Engineering"
MECH = "Mechanical Engineering"
AERO = "Aerospace Engineering"
ESET = "Electronic Systems Engineering Technology (ESET)"
MATH = "Mathematics"
PHYS = "Physics"
STAT = "Statistics"
BIO = "Biology"
CHEMISTRY = "Chemistry"
MAJOR_OTHER = "Other"
MAJORS = [
    (CS, "Computer Science"),
    (CE, "Computer Engineering"),
    (COMP, "Computing"),
    (EE, "Electrical Engineering"),
    (MIS, "Management Information Systems"),
    (DS, "Data Science/Engineering"),
    (GENE, "General Engineering"),
    (BMEN, "Biomedical Engineering"),
    (CHEM, "Chemical Engineering"),
    (CIVIL, "Civil Engineering"),
    (INDU, "Industrial Engineering"),
    (MECH, "Mechanical Engineering"),
    (AERO, "Aerospace Engineering"),
    (ESET, "Electronic Systems Engineering Technology (ESET)"),
    (MATH, "Mathematics"),
    (PHYS, "Physics"),
    (STAT, "Statistics"),
    (BIO, "Biology"),
    (CHEMISTRY, "Chemistry"),
    (MAJOR_OTHER, "Other"),
]
DISCOVERY_METHOD_OPTIONS = [
    ("Friend", "From a friend"),
    ("Tabling", "Tabling outside Zachry"),
    ("Howdy Week", "From Howdy Week"),
    ("Yard Sign", "Yard sign"),
    ("Social Media", "Social media"),
    ("Student Orgs", "Though another student org"),
    ("TH Organizer", "From a TAMUhack organizer"),
    ("ENGR Newsletter", "From the TAMU Engineering Newsletter"),
    ("MLH", "Major League Hacking (MLH)"),
    ("Attended Before", f"I've attended {settings.EVENT_NAME} before"),
]
PURPOSE_WIN = "W"
PURPOSE_LEARN = "L"
PURPOSE_WORKSHOP = "WR"
PURPOSE_RECRUITING = "R"
PURPOSE_MESS_AROUND = "M"
PURPOSE_OPTIONS = [
    (PURPOSE_WIN, "I want to win!"),
    (PURPOSE_LEARN, "I want to learn something new!"),
    (PURPOSE_WORKSHOP, "I just want to attend all the workshops"),
    (
        PURPOSE_RECRUITING,
        "I just want to talk to the sponsors and get a job",
    ),
    (PURPOSE_MESS_AROUND, "I want to have a fun weekend with my friends!"),
]
WARECHOICE = [("SW", "Software"), ("HW", "Hardware")]


COUNTRIES = [
    "United States of America",
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia (Plurinational State of)",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei Darussalam",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo",
    "Congo, Democratic Republic of the",
    "Costa Rica",
    "Cote d'Ivoire",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran (Islamic Republic of)",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea (Democratic People's Republic of)",
    "Korea, Republic of",
    "Kuwait",
    "Kyrgyzstan",
    "Lao People's Democratic Republic",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Micronesia (Federated States of)",
    "Moldova, Republic of",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russian Federation",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syrian Arab Republic",
    "Tajikistan",
    "Tanzania, United Republic of",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkiye",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom of Great Britain and Northern Ireland",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela (Bolivarian Republic of)",
    "Viet Nam",
    "Yemen",
    "Zambia",
    "Zimbabwe",
]

COUNTRIES_TUPLES = [(c, c) for c in COUNTRIES]
