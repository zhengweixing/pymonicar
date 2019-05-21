from . import auth
from flask import redirect,url_for,request,render_template,abort
from flask_login import logout_user, login_user,current_user,login_required
from .forms import LoginForm,RegisterForm
from ..models import User
from .. import db
from ..wxhanders import from_qiye, from_gongzhong


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/ucenter', methods=['GET', 'POST'])
@login_required
def ucenter():
    return render_template('userinfo.html', title=current_user.username+'-用户中心')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('auth.ucenter'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.uid.data).first()
        if user is not None and user and user.verify_password(login_form.pwd.data):
            login_user(user, login_form.remember_me.data)
            return redirect(request.args.get('next') or url_for('auth.ucenter'))
        else:
            return render_template('login.html', title='用户登录', form=login_form, error='登录失败，账号或密码错误！')
    return render_template('login.html', title='用户登录', form=login_form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('auth.ucenter'))
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User.query.filter_by(username=register_form.uid.data).first()
        if user is not None:
            return render_template('register.html', title='用户注册', form=register_form, error='用户名已经占用，请重新取名！')
        else:
            user = User(username=register_form.uid.data, phone=register_form.tel.data, email=register_form.email.data)
            user.set_password(register_form.pwd.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(request.args.get('next') or url_for('auth.ucenter'))
    return render_template('register.html', title='用户注册', form=register_form)


@auth.route('/bind/<int:where_from>/<who>', methods=['GET', 'POST'])
def bind(where_from, who):
    if (where_from == from_gongzhong or where_from == from_qiye) and not who.strip()=='':
        if current_user and current_user.is_authenticated:
            if where_from == from_qiye:
                current_user.qywechatid = who
            elif where_from == from_gongzhong:
                current_user.gzwechatid = who
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('auth.ucenter'))
        else:
            return render_template('userinfo.html', title='用户绑定', modal={'title':'提示','message':'您需要登录才能完成绑定！','buttons':['<a class="btn btn-primary" href="/login?next=/bind/{0}/{1}">前往登录</a>'.format(where_from,who)]})
    abort(403)


