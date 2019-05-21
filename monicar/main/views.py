#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import main
from flask import request, Response, render_template, session
from .forms import StudentForm, YuYueForm
from flask_login import current_user, login_user
from ..student import page_format, login_student, yuyue_login, save_students_db, get_hou_jiao_fei, get_wei_wan_cheng, get_wei_jiao_fei, get_yi_jiao_fei, get_yi_wan_cheng
from ..wxhanders import wx_login_to_web
from ..webclient import CheShang, JiaoTong


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='学时系统')


@main.route('/format', methods=['POST'])
def format():
    url = request.values['url']
    re = request.values['re']
    body = request.values['body']
    return page_format(url, re, body)


@main.route('/check_code', methods=['GET', 'POST'])
def check_code():
    where = request.args.get('from')
    try:
        if where == 'cheshang':
            control = CheShang()
            res = control.get_check_code()
        elif where == '122gov':
            control = JiaoTong()
            res = control.get_check_code()
        else:
            raise Exception('args is error')
        session['control'] = control.encode() if control else ''
        return Response(res.content, mimetype='image/jpeg')
    except Exception as e:
        return 'ERROR'


@main.route('/mgr_stu', methods=['GET','POST'])
@wx_login_to_web
def mgr_stu():
    act = request.args.get('act', 'weiwancheng')
    if current_user and current_user.is_authenticated:
        if request.method == 'POST':
            stuid = request.values['stuid']
            check_code = request.values['checkcode']
            result = login_student({'xue_shi_type':2, 'stuid':stuid, 'check_code':check_code})
            return result
        page = request.args.get('page', 1, type=int)
        students = None
        if act == 'weiwancheng':
            title, pagination, students = get_wei_wan_cheng(current_user,page=page)
        elif act == 'yiwancheng':
            title, pagination, students = get_yi_wan_cheng(current_user,page=page)
        elif act == 'weijiaofei':
            title, pagination, students = get_wei_jiao_fei(current_user,page=page)
        elif act == 'houjiaofei':
            title, pagination, students = get_hou_jiao_fei(current_user,page=page)
        elif act == 'yijiaofei':
            title, pagination, students = get_yi_jiao_fei(current_user,page=page)
        return render_template('mgrstu.html', title = title, students=students,  pagination=pagination)
    return render_template('mgrstu.html', title = '学员管理', modal={'title':'温馨提示','message':'您需要登录才能查看！','buttons':['<a class="btn btn-primary" href="/login?next=/mgr_stu?act={0}">前往登录</a>'.format(act)]})


@main.route('/add_stu', methods=['GET', 'POST'])
@wx_login_to_web
def add_stu():
    title = '新增学员'
    student_form = StudentForm()
    if student_form.validate_on_submit():
        whoadd = current_user if current_user and current_user.is_authenticated else student_form.uid.data
        student = {'stuid': student_form.uid.data, 'stupwd': student_form.pwd.data, 'cardno': student_form.card_no.data,
                   'carpwd': student_form.card_pwd.data, 'xue_shi_type' : student_form.xue_shi_type.data, 'check_code':student_form.check_code.data}
        student = login_student(student)
        if student:
            user, s = save_students_db(student, 'from_web', whoadd)
            msg = s+'<br/><br/>若提示新增成功，可点击查看<a href="{0}">详细信息</a>，然后联系我进行启动系统<hr/>微信: <strong>zh-12306</strong><br/>QQ: <strong><a href="tencent://message/?uin=529459515">529459515</a></strong>'.format('/mgr_stu?act=weijiaofei')
            student_form.clearn()
            if current_user and current_user.is_authenticated:
                pass
            else:
                login_user(user,True)
        else:
            msg = '新增失败，请再次提交，或联系：QQ:529459515 微信：zh-12306'
        return render_template('addstu.html', title=title, form=student_form, modal={'title':'新增结果','message':msg})
    return render_template('addstu.html', title=title, form=student_form)


@main.route('/122gov', methods=['GET', 'POST'])
@wx_login_to_web
def yuyue():
    title = '预约系统登录'
    student_form = YuYueForm()
    if student_form.validate_on_submit():
        whoadd = current_user if current_user and current_user.is_authenticated else student_form.uid.data
        student = {'stuid': student_form.uid.data, 'stupwd': student_form.pwd.data, 'check_code':student_form.check_code.data}
        student = yuyue_login(student)
        msg = student['msg']
        return render_template('yuyue.html', title=title, form=student_form, modal={'title':'新增结果','message':msg})
    return render_template('yuyue.html', title=title, form=student_form)


@main.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help.html', title='使用教程')