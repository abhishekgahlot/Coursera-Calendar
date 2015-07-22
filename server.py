import requests
import urllib
from uuid import uuid4
from bottle import route, run, template, request


url = 'https://accounts.coursera.org/oauth2/v1/auth'
url1 = 'https://accounts.coursera.org/oauth2/v1/token'

CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:41812/callback"
access_token = None
nonce = None

@route('/nonce/<local_token>')
def index(local_token):
	text = '<a href="%s">Authenticate with coursera</a>'
	global nonce
	nonce = local_token
	return text % make_authorization_url()
	
	
def make_authorization_url():
    state = str(uuid4())
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "view_profile"}
    url = "https://accounts.coursera.org/oauth2/v1/auth?" + urllib.urlencode(params)
    return url


@route('/callback')
def coursera_callback():
		client_auth = requests.auth.HTTPBasicAuth("S4z1dv7EMJgm_HoQv_p1UQ", "uuKKV8jTgTd8muHJrJyvtw")
		post_data = {
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET,
					"code": str(request.query['code']),
					"redirect_uri": REDIRECT_URI,
					"grant_type": "authorization_code"
					}
		response = requests.post(url1,
								auth=client_auth,
								data=post_data)
		token_json = response.json()
		global access_token
		access_token = token_json 
		return str('Close the window')

@route('/access_token/<local_token>')
def access_token(local_token):
	global nonce
	global access_token
	if nonce == '':
		return 'expired'
	if nonce == local_token and nonce != '':
		nonce = ''
		return str(access_token)
	else:
		return 'Token mismatch'
		
		
run(host='localhost', port=41812)
