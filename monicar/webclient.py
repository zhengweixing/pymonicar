from threading import Thread, RLock
from . import weichat
import requests
import random, math
import re, hashlib, json, time
import traceback
from . import db


def log(message):
    message = '{0}:{1}'.format(time.strftime('"%Y-%m-%d %H:%M:%S"'), message)
    print(message)


def send_wx(message):
    log(message)
    message = '{0}:{1}'.format(time.strftime('"%Y-%m-%d %H:%M:%S"'), message)
    weichat.client().message.send_text('0', 'Zh-12306', message)


def page_format(url, page):
    result = {}
    groups = re.compile(r'<td>([^<]+)[^>]*[^<]+?', re.M).findall(page.replace('\r\n', '').replace('\t', ''))
    if len(groups) >= 15:
        result['IdCard'] = groups[6]
        result['StuName'] = groups[4]
        result['CarTypeName'] = groups[8]
        result['Phone'] = groups[12]
        result['DrsName'] = groups[10]
        result['Email'] = groups[14]
        result['complete_time'] = groups[15]
        result['state'] = True
    return result


class WebClient(object):
    __proxies = {
         #"http": "http://1424889754667295_default_54:r6k66jgdu5@10.242.175.127:3128/"
    }

    def __init__(self, **kwargs):
        if 'cookies' in kwargs:
            self.cookies = kwargs['cookies']
        else:
            self.cookies = {}

    def set_cookies(self, cookies):
        for name, value in cookies.items():
            self.cookies[name] = value

    def __update_cookies(self, res):
        for name, value in res.cookies.items():
            self.cookies[name] = value

    def get(self, url, params=None, **kwargs):
        if 'cookies' in kwargs:
            self.set_cookies(kwargs['cookies'])
            del kwargs['cookies']
        res = requests.get(url, params, cookies=self.cookies, proxies = self.__proxies, **kwargs)
        try:
            res.raise_for_status()
            self.__update_cookies(res)
            return res
        except Exception as e:
            raise e

    def post(self, url, data=None, json=None, **kwargs):
        if 'cookies' in kwargs:
            self.set_cookies(kwargs['cookies'])
            del kwargs['cookies']
        res = requests.post(url, data, json, cookies=self.cookies, proxies=self.__proxies, **kwargs)
        try:
            res.raise_for_status()
            self.__update_cookies(res)
            return res
        except Exception as e:
            raise e


class Worker(Thread):

    def __init__(self, control):
        super(Worker, self).__init__()
        self.__control = control

    def run(self):
        self.__control.do()


class Control(object):

    def encode(self):
        return json.dumps(self.client.cookies)

    def decode(self, s):
        self.client.cookies = json.loads(s)

    def __init__(self):
        self.client = WebClient()

    def do(self):
        print('doing...')


class JiaoTong(Control):

    __check_code_url = 'https://gd.122.gov.cn/captcha1?nocache=' + str(random.random())

    def __init__(self):
        super(JiaoTong, self).__init__()
        self.client.get('https://gd.122.gov.cn', verify = False)

    def get_check_code(self):
        return self.client.get(self.__check_code_url, verify = False)


playlist = None


class CheShang(Control):
    __user = None
    __check_code_url = 'http://www.dgcheshang.cn/servlet/validate_image?' + str(random.random())

    def get_check_code(self):
        return self.client.get(self.__check_code_url)

    def login(self, user):
        # loginType=1&password=b2d368728dc5ff31c2051e5261eeb40a&loginId=500230198605101589&clear_password=101589&rand=5766
        url = 'http://www.dgcheshang.cn/platform/login!login.action'
        pwd = hashlib.md5(user['stupwd'].encode('utf-8')).hexdigest()
        data = {'loginType': 1,
                'password': pwd,
                'loginId': user['stuid'],
                'clear_password': user['stupwd'],
                'rand': user['check_code']}
        try:
            res = self.client.post(url, data)
            url = 'http://www.dgcheshang.cn/platform/loginAuthStudent.action'
            res = self.client.get(url)
            groups = re.compile(r'<td>([^<]+)[^>]*[^<]+?', re.M).findall(res.text.replace('\r\n','').replace('\t',''))
            if len(groups) >= 15:
                user['IdCard'] = user['stuid']
                user['StuName'] = groups[4]
                user['Password'] = user['stupwd']
                user['CarTypeName'] = groups[8]
                user['Phone'] = groups[12]
                user['DrsName'] = groups[10]
                user['Email'] = groups[14]
                user['complete_time'] = groups[15]
                user['state'] = True
            else:
                user['state'] = False
                user['msg'] = '请确认你的身份证号和密码准确无误，或根据下方联系方式联系我！'
        except requests.RequestException as reqe:
            user['state'] = False
            user['msg'] = '重新登录试试，服务器返回状态码：{0}'.format(reqe.args[0])
        return user

    def start(self, user):
        self.__user = user
        Worker(self).start()

    @staticmethod
    def __get_playlist():
        global playlist
        if playlist is None:
            path = 'monicar/static/dgcheshang_playlist.json'
            playlist = json.load(open(path, 'r', encoding='utf-8'))

    def get_current(self):
        self.__user.flashIndex = random.randint(0, 315) if self.__user.flashIndex is None or self.__user.flashIndex + 1 >= len(playlist) else self.__user.flashIndex + 1
        return playlist[self.__user.flashIndex]

    def do(self):
        self.__user.is_run = True;
        self.__get_playlist()
        begin_url = 'http://www.dgcheshang.cn/student/videoInfo!videoStudyBegin.action'
        end_url = 'http://www.dgcheshang.cn/student/videoInfo!videoStudyEnd.action'
        while True:
            try:
                play = self.get_current()
                spid = play['spid']
                seconds = math.ceil(play['time'])
                if seconds:
                    seconds += 10
                    res = self.client.post(begin_url, {'vid':spid}, cookies={'watchTime':'null'})
                    # {"kjurl":"http://www.dgcheshang.cn:9999/video/km3/3021202","pxkssj":"VsvHPI9P9d53ntbsX2poqEJBbMfDTIaI","fourTime":"0","allTime":"2"}
                    b_res = res.json()
                    if b_res['fourTime'] == '-1':
                        # 您当天已经学满4小时，本次视频将不计入学时
                        self.__user.is_complete_four = True
                        msg = '{0}当天已经学满4小时'.format(self.__user.name)
                        send_wx(msg)
                        break
                    elif b_res['fourTime'] == '1':
                        # 您已经学满24小时，本次视频将不计入学时
                        self.__user.is_complete = True
                        msg = '{0}已经学满24小时'.format(self.__user.name)
                        send_wx(msg)
                        break
                    else:
                        if b_res['pxkssj']:
                            log('{0}开始观看：《{1}》'.format(self.__user.name, play['title']))
                            time.sleep(seconds)
                            # vid=3021202&kssj=VsvHPI9P9d53ntbsX2poqEJBbMfDTIaI&xxsc=94
                            res = self.client.post(end_url, {'vid': spid, 'kssj':b_res['pxkssj'], 'xxsc':seconds })
                            e_res = res.json()
                            if e_res['studyFlag'] == '1':
                                msg = '{0}学时保存失败:\n{1}'.format(self.__user.name, res.text)
                                log(msg)
                            elif e_res['studyFlag'] == '0':
                                log('{0}完成视频：《{1}》'.format(self.__user.name, play['title']))
                            else:
                                msg = '{0}在完成视频《{1}》时，服务器返回了:\n{2}'.format(self.__user.name, play['title'], res.text)
                                log(msg)
                        else:
                            msg = '{0}在开始视频《{1}》时，服务器返回了:\n{2}'.format(self.__user.name, play['title'], res.text)
                            log(msg)
            except requests.RequestException as e:
                msg = '{0}请求失败，服务器返回:{1}'.format(self.__user.name, e.args[0])
                send_wx(msg)
            except Exception as e:
                msg = '{0}线程退出，[{1}]原因:\n{2}'.format(self.__user.name, type(e), e.args[0])
                send_wx(msg)
                break
        self.__user.is_run = False;
