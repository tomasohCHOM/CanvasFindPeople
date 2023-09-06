from canvasapi import Canvas
from canvasapi.course import Course, Assignment

CANVAS_API_URL = "https://canvas.instructure.com/"


def test_key(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    canvas.get_current_user()


def list_courses(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    user = canvas.get_current_user()
    courses = []

    for course in user.get_courses(enrollment_state="active"):
        if course.name == "Passport to Canvas":
            continue
        courses.append(course)
    return courses


def get_people(api_key):
    courses = list_courses(api_key)
    people = []
    for course in courses:
        for user in course.get_users():
            people.append(user)
    return people
