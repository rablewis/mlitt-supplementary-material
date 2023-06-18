import http.cookiejar
import urllib.parse
import urllib.request

def with_command_line_credentials():
    username = input('OxCal username: ')
    password = input('OxCal password: ')

    cookie_jar = with_credentials(username, password)
    return cookie_jar

def with_credentials(username, password):
	login_url = 'https://c14.arch.ox.ac.uk/login/login.php?Location=%2Foxcalold%2FOxCal.html'
	login_data = {'Action': 'Login', 'Location': '/oxcalold/OxCal.html', 'UserName': username, 'PassWord': password}
	login_data = urllib.parse.urlencode(login_data)
	login_data = login_data.encode('utf-8')

	cj = http.cookiejar.CookieJar()
	usernameCookie = http.cookiejar.Cookie(
		version=1,
		name='OxCalUserName', 
		value=username, 
		port=None, port_specified=False,
		domain='c14.arch.ox.ac.uk', domain_specified=True, 
		domain_initial_dot=False,
		path='/', path_specified=True, 
		secure=False,
		expires=None,
		discard=False,
		comment=None,
		comment_url=None,
		rest={},
		rfc2109=False)
	cj.set_cookie(usernameCookie)

	login_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
	login_resp = login_opener.open(login_url, data=login_data)

	return cj
