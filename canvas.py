from canvasapi import *

CANVAS_API_URL = "https://canvas.instructure.com/"


def test_key(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    canvas.get_current_user()


def get_courses(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    user = canvas.get_current_user()
    courses = []

    for course in user.get_courses(enrollment_state="active"):
        if course.name == "Passport to Canvas":
            continue
        courses.append(course)
    return courses


def get_users_from_course(course):
    people = []
    for user in course.get_users():
        people.append(user)
    return people


def get_all_users(api_key):
    courses = get_courses(api_key)
    people = []
    for course in courses:
        for user in course.get_users():
            people.append(user)
    return people


def search_user_in_course(course, searched_user):
    found_users = []
    for user in course.get_users():
        if searched_user.lower() in user.name.lower():
            found_users.append((user, course))
    return found_users


def search_user_in_all(searched_user, api_key):
    courses = get_courses(api_key)
    found_users = []
    for course in courses:
        found_users.extend(search_user_in_course(course, searched_user))
    return found_users


def search_user_by_last_name(course, searched_user):
    pass
