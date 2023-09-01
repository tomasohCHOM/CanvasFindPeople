from canvasapi import *

CANVAS_API_URL = "https://canvas.instructure.com/"


def test_key(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    canvas.get_current_user()


def list_courses(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    user = canvas.get_current_user()
    courses = []

    for course in user.get_courses():
        courses.append(course)
    return courses


def get_people_from_course(course):
    people = []
    for user in course.get_users():
        people.append(user)
    return people
