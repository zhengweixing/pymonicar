import re, hashlib
from flask import session
import json, requests, datetime
from .models import Student,User
from . import db
from six import string_types
from . import weichat
from .webclient import CheShang
from .webclient import page_format as pf

"""
student : {'web_whoadd|qy_whoadd|gz_whoadd':'', 'stuid':'', 'stupwd':'', 'cardno':'', 'carpwd':''}
"""


def get_shenfenzheng(msg):
    pattern = re.compile(r'([1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X))', re.M)
    groups = pattern.findall(msg)
    ids = []
    for group in groups:
        stuid = group[0]
        stupwd = stuid[-6:]
        ids.append({'stuid':stuid, 'stupwd':stupwd, 'cardno':'', 'carpwd':''})
    return ids if len(ids) >0 else None


def login_students(students):
    if students:
        url = 'http://114.215.103.152:8081/monicar?act=addstudent'
        data = {'app':'pymonicar','data':json.dumps(students)}
        res = requests.post(url,data)
        try:
            res.raise_for_status()
        except requests.RequestException as reqe:
            print(reqe)
            return False
        return res.json()


def yuyue_login(student):
    """
    usertype=1&systemid=main&username=421022198501150650&password=Yone520&captcha=D3Q8&rememberMe=true

    """
    url = 'https://gd.122.gov.cn/user/m/login'
    cookies = session['cookies']
    data = {'usertype': 1, 'systemid':'main', 'password': student['stupwd'], 'username': student['stuid'], 'captcha': student['check_code'], 'rememberMe': True}
    res = requests.post(url, data, cookies=cookies, verify=False)
    try:
        res.raise_for_status()
        for name, value in res.cookies.items():
            cookies[name] = value
        student['state'] = False
        student['msg'] = res.text
    except requests.RequestException as reqe:
        student['state'] = False
        student['msg'] = reqe
    return student


def login_student(student):
    type = student['xue_shi_type']
    if type == 0:
        # 悦驾网
        student['Citycode'] = '121000'
        student['school'] = '121000'
        students = login_students([student])
        if students:
            return students[0]
    else:
        control = CheShang()
        control.decode(session['control'])
        if type == 1:
            # 车尚网
            student['Citycode'] = '121001'
            return control.login(student)
        elif type == 2:
            o = Student.query.filter_by(id=student['stuid']).first()
            student['stuid'] = o.student_id
            student['stupwd'] = o.password
            res = control.login(student)
            if res['state']:
                o.complete_time = res['complete_time']
                #db.session.add(o)
                #db.session.commit()
                control.start(o)
                return json.dumps({'result':True, 'msg':'启动操作成功！{0}当前学时是{1}'.format(o.name, o.complete_time)})
            else:
                return json.dumps({'result':False, 'msg':res['msg']})


"""
[{'RefStuCode': '6120140303048',
'Addr': None,
'state': True,
'ActivedTime': None,
'BranchId': 0,
'ExpireTime': '/Date(1491651368000)/',
'Photo': None,
'UserId': 924,
'StuId': 31395,
'StuName': '郑伟星',
'UpdTime': '/Date(1396337960000)/',
'Batch': 1,
'Phone': '15899912449',
'CarTypeName': 'C1',
'StudyTypeId': 2,
'CrtTime': '/Date(1396337960000)/',
'IdCard': '420982198910133258',
'States': 1,
'Sex': 0,
'StuCode': '420982198910133258',
'Birthday': '/Date(624211200000)/',
'DrsName': '东莞市东富机动车驾驶员培训有限公司',
'UpdUser': '计时系统导入',
'Nation': '汉',
'IdCardType': 0,
'DrsId': 2091,
'CrtUser': '计时系统导入',
'AppType': 3,
'IntoType': 1,
'Pwd': '506787892bc211855265020b5042a1fd',
'Email': '529459515@qq.com'}]
"""


def save_student_db(student ,whoadd):
    if student['state']:
        student_id=student['IdCard']
        if not Student.query.filter_by(student_id=student_id).first():
            student_obj = Student(student_id=student_id,
                                  name=student['StuName'],
                                  password=student['Password'],
                                  tel=student['Phone'],
                                  School=student['DrsName'],
                                  email=student['Email'],
                                  car_type=student['CarTypeName'],
                                  time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  is_pay=0,
                                  citycode=student['Citycode'],
                                  complete_time= student['HaveTime'] if 'HaveTime' in student else '等待获取学时',
                                  is_complete=False,
                                  user=whoadd)
            try:
                update_student(student_obj)
            except Exception as e:
                return '新增学员{0}失败,身份证：{1}，原因{2}'.format(student['StuName'],student_id, str(e))
            return '学员{0}新增成功！'.format(student['StuName'])
        else:
            return '数据库中已经存在{0},身份证号：{1}'.format(student['StuName'],student_id)
    else:
        return '{0}新增失败,{1}'.format(student['stuid'],student['msg'])


def save_students_db(students, where_from, whoadd):
    result=''
    msgs=[]
    if isinstance(whoadd, string_types):
        user = User.query.filter_by(username=whoadd).first()
        if user is None:
            whoadd = User(username=whoadd, gzwechatid=whoadd, qywechatid=whoadd)
            if where_from == "from_web":
                whoadd.set_password('123456')
            else:
                whoadd.set_password('123456')
        else:
            whoadd = user
        db.session.add(whoadd)
    if isinstance(students, dict):
        msgs = save_student_db(students, whoadd)
        result = '\n' + msgs
    elif isinstance(students, list):
        for student in students:
            msg = save_student_db(student, whoadd)
            msgs.append(msg)
            result = result + '\n' + msg
    weichat.client().message.send_text('0','Zh-12306','{0}从{1}新增了学员,结果如下:\n{2}'.format(whoadd.username, where_from, result))
    if where_from=='from_web':
        return whoadd, msgs
    else:
        return  msgs


def update_student(student):
    db.session.add(student)
    db.session.commit()


def get_wei_jiao_fei(current_user, page=1, per_page=8):
    pagination =  current_user.get_students(is_pay=0).paginate(page, per_page=per_page,error_out=False)
    return '未缴费学员', pagination,pagination.items


def get_yi_jiao_fei(current_user,page=1, per_page=8):
    pagination = current_user.get_students(is_pay=1).paginate(page, per_page=per_page,error_out=False)
    return '已缴费学员',pagination,pagination.items


def get_hou_jiao_fei(current_user,page=1, per_page=8):
    pagination =  current_user.get_students(is_pay=2).paginate(page, per_page=per_page,error_out=False)
    return '后缴费学员',pagination,pagination.items


def get_wei_wan_cheng(current_user,page=1, per_page=8):
    pagination = current_user.get_students(is_complete=False).paginate(page, per_page=per_page,error_out=False)
    return '未完成学员',pagination,pagination.items


def get_yi_wan_cheng(current_user,page=1, per_page=8):
    pagination = current_user.get_students(is_complete=True).paginate(page, per_page=per_page,error_out=False)
    return '已完成学员',pagination,pagination.items


def page_format(url, pattern, body):
    if url == 'http://www.dgcheshang.cn/platform/loginAuthStudent.action':
        result = pf(url,body)
        return json.dumps(result)
    elif url =='http://www.dgcheshang.cn/platform/login!login.action':
        result = re.compile(r'/platform/loginAuthStudent.action', re.M).findall(body)
        if result:
            return json.dumps({ "state": 1, "url":'http://www.dgcheshang.cn/platform/loginAuthStudent.action'})
        result = re.compile(r"激活帐号", re.M).findall(body)
        if result:
            return json.dumps({ "state": -1, "msg":"请使用学习卡激活帐号！"})
        return json.dumps({"state":0, "msg":"服务器返回超过预期内容!"})
    elif url == 'http://www.dgcheshang.cn/student/studentInfo!activeXyAccount.action':
        return json.dumps({"state":True, "msg":"激活成功！"})


