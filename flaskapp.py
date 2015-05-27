from flask import Flask , request
import requests
import requests.auth
from uuid import uuid4
import urllib


url = 'https://accounts.coursera.org/oauth2/v1/auth'
url1 = 'https://accounts.coursera.org/oauth2/v1/token'

CLIENT_ID = "S4z1dv7EMJgm_HoQv_p1UQ"
CLIENT_SECRET = "uuKKV8jTgTd8muHJrJyvtw"
REDIRECT_URI = "http://localhost:41812/callback"
access_token = ''
nonce = ''

app = Flask(__name__)


@app.route('/nonce/<local_token>')
def homepage(local_token):
    text = '<a href="%s">Authenticate with coursera</a>'
    global nonce
    nonce = str(local_token)
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


@app.route('/callback')
def coursera_callback():
		client_auth = requests.auth.HTTPBasicAuth("S4z1dv7EMJgm_HoQv_p1UQ", "uuKKV8jTgTd8muHJrJyvtw")
		post_data = {
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET,
					"code": str(request.args.getlist('code')[0]),
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

@app.route('/access_token/<local_token>')
def access_token(local_token):
	global nonce
	global access_token
	if nonce == local_token and nonce != '':
		nonce = ''
		return str(access_token)
	else:
		return 'Token mismatch'
		

if __name__ == '__main__':
    app.run(debug=True, port=41812)