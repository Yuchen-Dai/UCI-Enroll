import requests


ucinetid = None
password = None




requests.packages.urllib3.disable_warnings()


account = requests.session()
enrollment = None
timeout = 30

def post()-> str:
    global enrollment_url
    
    text = requests.get('https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh', verify = False, timeout = timeout).text
    enrollment_url = _get_url(text)
    return_url = enrollment_url.split('=', 1)[1].split('&')[0]

    headers = {
       'Connection': 'keep-alive',
       'Cache-Control': 'max-age=0',
       'Origin' : 'https://login.uci.edu',
       'Upgrade-Insecure-Requests': '1',
       'Content-Type': 'application/x-www-form-urlencoded',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
       'Referer': enrollment_url,
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'zh-CN,zh;q=0.9'
       }
    d = {
         'referer': '',
         'return_url': return_url,
         'info_text': '',
         'info_url': '',
         'submit_type': '',
         'ucinetid': ucinetid,
         'password': password,
         'login_button':'Login'}
    req = account.post(enrollment_url, data = d, headers = headers, verify = False, timeout = timeout)

    cookie = _get_ucinetid_auth(req.headers['Set-Cookie'])
    if cookie == None:
        return

    
    url = _get_url(req.text)
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'referer': url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie
        }
    req2 = account.get(url, headers = headers, verify = False, timeout = timeout)

    base_url = enrollment_url.split('?',2)[1][11:]
    call = _get_call()
    headers = {
        'Host': _get_host(base_url),
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie
        }
    d = (
        ('page', 'enrollQtrMenu'),
        ('mode', 'enrollmentMenu'),
        ('call', call),
        ('submit','Enrollment Menu')
        )
    req3 = account.post(base_url, headers = headers, data = d, verify = False, timeout = timeout)
    if "logged out" in req3.text:
        return
    return cookie

def have_space(coursecode)->bool:
    #######################################
    # YearTerm must be update every time !#
    #######################################
    data = {'ShowFinals': 'on', 'ShowComments': 'on', 'CancelledCourses': 'Exclude', 'Submit': 'Display Text Results', 'Web': 'Results', 'Dept': 'ALL',\
            'Division': 'ANY', 'Breadth': 'ANY', 'FullCourses': 'ANY', 'ClassType': 'ALL', 'YearTerm': '2020-03', 'CourseNum': None, 'FontSize': '100', 'EndTime': None, \
        'InstrName': None, 'MaxCap': None, 'Room': None, 'Days': None, 'CourseTitle': None, 'StartTime': None, 'CourseCodes': coursecode, 'Units': None, 'Bldg': None}
    resp = requests.post('https://www.reg.uci.edu/perl/WebSoc', data=data)
    for i in resp.text.split('\n'):
        i = i.lower()
        if coursecode in i and 'open' not in i:
            return False
    return True

def enroll(cookie, coursecode)-> bool:
    base_url = enrollment_url.split('?',2)[1][11:]
    call = _get_call()

    headers = {
        'Host': _get_host(base_url),
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': base_url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie
        }
    d = (
        ('page', 'enrollmentMenu'),
        ('call', call),
        ('button', 'Send Request Mode'),
        ('mode', 'add'),
        ('courseCode', coursecode),
        ('gradeOption', ''),
        ('varUnits', ''),
        ('authCode', ''),
        ('courseCode', '')
        )
    r = account.post(base_url, data = d, headers = headers, verify = False, timeout = timeout)
    return ('have added' in r.text) or ('TENTATIVELY ADDED' in r.text)

def log_off(cookie):
    base_url = enrollment_url.split('?',2)[1][11:]
    call = _get_call()
    headers = {
        'Host': _get_host(base_url),
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': base_url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie
        }
    d = (
        ('page', 'enrollmentMenu'),
        ('mode', 'exit'),
        ('call', call),
        ('submit', 'Logout')
        )
    r = account.post(base_url, data = d, headers = headers, verify = False, timeout = timeout)
    
def _get_url(context)-> str:
    for i in context.split('"'):
        if 'url=' in i:
            return i.split('=', 1)[1]

def _get_ucinetid_auth(cookie)-> str:
    keys = cookie.split(';')
    for key in keys:
        if 'ucinetid_auth' in key:
            return key

def _get_call()-> str:
    index = enrollment_url.index('call=')
    return enrollment_url[index+5:index + 9]

def _get_host(url)-> str:
    index = url.index('edu')
    return url[8:index+3]





