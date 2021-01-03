from requests import get, post
from os import environ
from pprint import pprint

KEY = environ["MOODLE_API_KEY"]
URL = environ["MOODLE_URL"]
ENDPOINT = "/webservice/rest/server.php"

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Adapted from https://github.com/mrcinv/moodle_api.py
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict == None:
        out_dict = {}
    if not type(in_args) in (list,dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == "":
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Adapted from https://github.com/mrcinv/moodle_api.py
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, "moodlewsrestformat": "json", "wsfunction": fname})
    response = post(URL+ENDPOINT, parameters)
    response = response.json()
    if type(response) == dict and response.get("exception"):
        raise SystemError("Error calling Moodle API\n", response)
    return response

calendar_data = call("core_calendar_get_calendar_upcoming_view")["events"]
minimal_data = [{"name": x["name"], "timestart": x["timestart"], "timemodified": x["timemodified"]} for x in calendar_data]
pprint(minimal_data)
