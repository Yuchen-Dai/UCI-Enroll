import pc, random, time, copy

attempt = 1
def user_interface():
    _get_account()
    courses = _get_course()
    while len(courses) > 0:
        start = time.clock()
        cookie = _log_in()
        while time.clock() - start < 500 and len(courses) > 0:
            _enroll(cookie, courses)
        _log_off(cookie)
    print('Successfully enroll in all courses.')
    input('Enter q to exit.')
    


def _get_account():
    try:
        with open('account.txt', 'r') as file:
            line = file.readline().split()
            pc.ucinetid = line[0]
            pc.password = line[1]
    except:
        pc.ucinetid = input('Ucinetid: ')
        pc.password = input('Password: ')
        with open('account.txt', 'w') as file:
            file.write(f'{pc.ucinetid} {pc.password}')

            
def _get_course()-> list:
    times = int(input('How many courses?: '))
    result = []
    for i in range(times):
        result.append(input(f'Course {i + 1}: '))
    return result


def _enroll(cookie, courses):
    global attempt
    coursess = copy.deepcopy(courses)
    for course in coursess:
        success = pc.enroll(cookie, course)
        if success:
            courses.remove(course)
            print(f'Enroll {course} success.')
        else:
            print(f'Enroll {course} fail. Attempt {attempt}.')
            attempt += 1
        time.sleep(random.randint(1,3))

def _log_in():
    cookie = None
    while cookie == None:
        try:
            print(f'Try to log in {pc.ucinetid}.')
            cookie = pc.post()
        except:
            print('Log in fail.Try log in again...\n...')
            time.sleep(random.randint(1,3))
    print(f'Log in success.')
    return cookie

def _log_off(cookie):
    print(f'Log off {pc.ucinetid}.')
    pc.log_off(cookie)

if __name__ == '__main__':
    user_interface()
