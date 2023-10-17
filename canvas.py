from canvasapi import *
import canvasapi.exceptions

CANVAS_API_URL = "https://canvas.instructure.com/"


def test_key(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    canvas.get_current_user()


def get_courses(api_key):
    canvas = Canvas(CANVAS_API_URL, api_key)
    user = canvas.get_current_user()
    courses = []

    for course in user.get_courses(enrollment_state="active"):
        # if "Passport" in course.name or "Title IX" in course.name:
        #     continue
        courses.append(course)
    return courses


def search_course(api_key, query):
    canvas = Canvas(CANVAS_API_URL, api_key)
    user = canvas.get_current_user()

    for course in user.get_courses(enrollment_state="active"):
        if query.lower() in str(course).lower():
            return course
    return None


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
        try:
            found_users.extend(search_user_in_course(course, searched_user))
        except canvasapi.exceptions.Forbidden:
            continue
    return found_users


def search_user_by_last_name(searched_user, api_key):
    courses = get_courses(api_key)
    found_users = []
    for course in courses:
        try:
            users = get_users_from_course(course)
        except canvasapi.exceptions.Forbidden:
            continue
        query_first_letter = searched_user[0]
        left, right = 0, len(users) - 1
        while left <= right:
            mid = (left + right) // 2
            if query_first_letter.lower() == users[mid].sortable_name[0].lower():
                start_pos = mid
                while (
                    start_pos != 0
                    and query_first_letter.lower()
                    == users[start_pos - 1].sortable_name[0].lower()
                ):
                    start_pos -= 1
                while (
                    query_first_letter.lower()
                    == users[start_pos].sortable_name[0].lower()
                ):
                    if searched_user.lower() in users[start_pos].sortable_name.lower():
                        found_users.append((users[start_pos], course))
                    start_pos += 1
                break

            elif ord(users[mid].sortable_name[0].lower()) > ord(
                query_first_letter.lower()
            ):
                right = mid - 1
            else:
                left = mid + 1
    return found_users
