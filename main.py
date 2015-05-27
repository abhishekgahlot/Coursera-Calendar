#Server dependencies
import json
import requests
import urllib
from uuid import uuid4
from bottle import Bottle, route, run, template, request


class Coursera:
    def __init__(self,access_token):
        self.enrollments_url = "https://api.coursera.org/api/users/v1/me/enrollments"
        self.auth_headers = {'Authorization': 'Bearer ' + access_token}
        self.enrollments = json.loads(requests.get(self.enrollments_url, headers = self.auth_headers).content)

    def get_course_sessions(self):
        self.coursesID = [ str(course['courseId']) for course in self.enrollments['enrollments'] if course['active'] and course['startStatus'] == 'Present']
        self.coursesSession = [ str(course['sessionId']) for course in self.enrollments['enrollments'] if course['active'] and course['startStatus'] == 'Present']
        self.coursesName = [course['name'] for course in self.enrollments['courses'] if str(course['id']) in self.coursesID]
        return self.coursesName

    def get_calendar_files(self):
        pass        


class Calendar:
    from json import JSONEncoder
import json
from datetime import datetime
import icalendar
from icalendar import Calendar, vDDDTypes, Event,vDatetime
#https://class.coursera.org/matrix-002/api/course/calendar

class ICalendarEncoder(JSONEncoder):
    def default(self, obj, markers=None):

        try:
            if obj.__module__.startswith("icalendar.prop"):
                return (obj.to_ical())
        except AttributeError:
            pass

        if isinstance(obj, datetime):
            return (obj.now().strftime('%d-%m-%YT%H:%M:%S'))

        return JSONEncoder.default(self,obj)    


cal = Calendar.from_ical(open('/Users/apple/calendar','rb').read())

for event in cal.walk(name="VEVENT"):
    suspect = json.dumps(event, cls=ICalendarEncoder)
    working = json.loads(suspect)
    print working,"\n"

print vDatetime.from_ical('20150319T035900Z','Asia/Kolkata')




class Server:
    def __init__(self,port = 41812):
        self._app = Bottle()
        self._host = 'localhost'
        self._port = port
        self._routes()
        self.CLIENT_ID = "S4z1dv7EMJgm_HoQv_p1UQ"
        self.CLIENT_SECRET = "uuKKV8jTgTd8muHJrJyvtw"
        self.REDIRECT_URI = "http://localhost:41812/callback"
        self.ACCESS_TOKEN = None
        self.nonce = False
        self.auth_url = "https://accounts.coursera.org/oauth2/v1/auth?"
        self.token_url = "https://accounts.coursera.org/oauth2/v1/token"

    def _routes(self):
        self._app.route('/nonce/<local_token>', callback=self.index_handler)
        self._app.route('/callback', callback=self.coursera_callback_handler)
        self._app.route('/access_token/<local_token>', callback=self.access_token_handler)

    def start(self):
        self._app.run(host=self._host, port=self._port)

    def index_handler(self,local_token):
        text = '<a href="%s">Authenticate with coursera</a>'
        self.nonce = local_token
        return text % self.authorization_url() , str(self.nonce) , str(type(self.nonce))

    def coursera_callback_handler(self):
        client_auth = requests.auth.HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET)
        payload = {
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "code": str(request.query['code']),
                    "redirect_uri": self.REDIRECT_URI,
                    "grant_type": "authorization_code"
                    }
        token_json = requests.post(self.token_url,auth=client_auth,data=payload).json()
        self.access_token = token_json
        return str('Close the window')


    def access_token_handler(self,local_token):
        if not self.nonce:
            return 'Expired'
        elif self.nonce == local_token:
            self.nonce = False
            return str(self.access_token)
        else:
            return 'Token mismatch'


    def authorization_url(self):
        state = str(uuid4())
        params = {"client_id": self.CLIENT_ID,
                    "response_type": "code",
                    "state": state,
                    "redirect_uri": self.REDIRECT_URI,
                    "duration": "temporary",
                    "scope": "view_profile"}
        return self.auth_url + urllib.urlencode(params)


Server().start()