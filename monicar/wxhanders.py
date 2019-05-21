#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from functools import wraps
from wxflask import create_reply,from_qiye,from_gongzhong
from flask import render_template,request
from . import weichat
from .models import User
from flask_login import login_user, current_user
from .student import get_shenfenzheng, login_students,save_students_db,get_hou_jiao_fei,get_wei_wan_cheng,get_wei_jiao_fei,get_yi_jiao_fei,get_yi_wan_cheng

user = None
token = None


@weichat.before_hand
def before_hand(where_from, msg):
    global token
    token = User.generate_token()[:6] + msg.source
    weichat.session.set(msg.source, True, 30)


def wx_login_to_web(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        print(request.user_agent)
        if current_user is None or not current_user.is_authenticated:
            where_from = request.args.get('where_from',type=int)
            local_token = request.args.get('token')
            if where_from is not None and local_token is not None:
                uid = local_token[6:]
                if weichat.session.get(uid):
                    local_user=None
                    if where_from == from_gongzhong:
                        local_user = User.query.filter_by(gzwechatid=uid).first()
                    elif where_from == from_qiye:
                        local_user = User.query.filter_by(qywechatid=uid).first()
                    if local_user:
                        print(local_user)
                        login_user(local_user, True)
        return fn(*args, **kwargs)
    return decorated_function


def login_required(fn):
    @wraps(fn)
    def wrap_function(where_from, msg, *args, **kwargs):
        global user
        if user:
            return fn(where_from, msg, *args, **kwargs)
        else:
            return bind(where_from,msg)
    return wrap_function


def user_required(fn):
    @wraps(fn)
    def wrap_function(where_from, msg, *args, **kwargs):
        global user
        if where_from == from_gongzhong:
            user = User.query.filter_by(gzwechatid=msg.source).first()
        elif where_from == from_qiye:
            user = User.query.filter_by(qywechatid=msg.source).first()
        return fn(where_from, msg, *args, **kwargs)
    return wrap_function


"""
根据消息类型注册处理函数
注册default_hander，将处理没有绑定的消息
"""


@weichat.register('default_hander')
def default_hand(where_from, msg):
    content = render_template('wx_default_reply.html', msg=msg)
    return create_reply(content, msg).render()


@weichat.register('text')
@user_required
def hand_text(where_from, msg):
    result = get_shenfenzheng(msg.content)
    if result is None:
        return default_hand(where_from,msg)
    students = login_students(result)
    resmsg = save_students_db(students, where_from, user if user and user.is_authenticated else msg.source)
    content = render_template('wx_default_reply.html',msg=msg, students=students, resmsg=resmsg)
    url = 'http://wx.ashufa.com/mgr_stu?act=weijiaofei&token={0}&where_from={1}&uid={2}'.format(token, where_from,msg.source)
    return create_reply([{'title':'新增学员结果如下','description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('image')
def hand_img(where_from, msg):
    menu_data = render_template('weixing_menu.txt')
    if where_from == from_gongzhong:
        result = weichat.client(where_from).menu.update(json.loads(menu_data))
        return create_reply(json.dumps(result), msg).render()
    elif where_from == from_qiye:
        result = weichat.client(where_from).menu.update(0,json.loads(menu_data))
        return create_reply(json.dumps(result), msg).render()
    else:
        return create_reply(msg.image, msg).render()


@weichat.register('subscribe')
def hand_subscribe(where_from, msg):
    description = '尊敬的{0}\n,非常感谢你的关注，为了更好的使用系统，请点击查看使用教程！'.format(msg.source)
    url = 'http://wx.ashufa.com/help'
    return create_reply([{'title':'使用帮助','description':description,'url':url,'image':'http://wx.ashufa.com/static/aboutus.jpg'}], msg).render()


@weichat.register('location')
def hand_location(where_from, msg):
    return create_reply("{0}，你当前位置：\n{1}".format(msg.source, msg.label), msg).render()


@weichat.register('addstudent')
def hand_student(where_from, msg):
    description = '尊敬的{0}\n请直接回复身份证号，进行学时代看！\n如果你未激活学习卡，可点击本消息进行激活\n如有疑问请加微信:zh-12306'.format('用户' if where_from==from_gongzhong else msg.source)
    url = 'http://wx.ashufa.com/add_stu?token={0}&where_from={1}'.format(token, where_from)
    return create_reply([{'title':'新增学员','description':description,'url':url,'image':'http://wx.ashufa.com/static/aboutus.jpg'}], msg).render()


@weichat.register('houjiaofei')
@user_required
@login_required
def hand_student(where_from, msg):
    url = 'http://wx.ashufa.com/mgr_stu?act=houjiaofei&token={0}&where_from={1}'.format(token, where_from)
    tit, p, students = get_hou_jiao_fei(user, page=1, per_page=30)
    content = render_template('wx_stu_mgr_reply.html', students=students, pagination=p, title=tit)
    return create_reply([{'title':tit,'description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('yijiaofei')
@user_required
@login_required
def hand_student(where_from, msg):
    url = 'http://wx.ashufa.com/mgr_stu?act=yijiaofei&token={0}&where_from={1}'.format(token, where_from)
    tit, p, students = get_yi_jiao_fei(user, page=1,per_page=30)
    content = render_template('wx_stu_mgr_reply.html', students=students, pagination=p, title=tit)
    return create_reply([{'title':tit,'description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('weijiaofei')
@user_required
@login_required
def hand_student(where_from, msg):
    url = 'http://wx.ashufa.com/mgr_stu?act=weijiaofei&token={0}&where_from={1}'.format(token, where_from)
    tit, p, students = get_wei_jiao_fei(user, page=1, per_page=30)
    content = render_template('wx_stu_mgr_reply.html', students=students, pagination=p, title=tit) + '\n加微信:zh-12306\n进行缴费后可立马代看！'
    return create_reply([{'title':tit,'description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('weiwancheng')
@user_required
@login_required
def hand_student(where_from, msg):
    url = 'http://wx.ashufa.com/mgr_stu?act=weiwancheng&token={0}&where_from={1}'.format(token, where_from)
    tit, p, students = get_wei_wan_cheng(user, page=1, per_page=30)
    content = render_template('wx_stu_mgr_reply.html', students=students, pagination=p, title=tit)
    return create_reply([{'title':tit,'description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('yiwancheng')
@user_required
@login_required
def hand_student(where_from, msg):
    url = 'http://wx.ashufa.com/mgr_stu?act=yiwancheng&token={0}&where_from={1}'.format(token, where_from)
    tit, p, students = get_yi_wan_cheng(user,page=1, per_page=30)
    content = render_template('wx_stu_mgr_reply.html', students=students, pagination=p, title=tit)
    return create_reply([{'title':tit,'description':content,'url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()


@weichat.register('bind')
def bind(where_from, msg):
    url = 'http://wx.ashufa.com/bind/{0}/{1}'.format(where_from,msg.source)
    return create_reply([{'title':'点击链接进行绑定','description':'点击本消息进入注册或绑定已有学时系统的帐号，绑定之后，你从微信新增的学员，都会添加到你的学时系统帐号下面！','url':url,'image':'http://wx.ashufa.com/static/df.jpg'}], msg).render()

'''--------------------------------------------------'''


