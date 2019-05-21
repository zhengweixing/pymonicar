__author__ = 'zwx'
from flask_wtf import Form
from wtforms import StringField,BooleanField,PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class LoginForm(Form):
    uid = StringField('帐号', validators=[DataRequired()])
    pwd = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我', default = False)
    submit = SubmitField('登录')


class RegisterForm(Form):
    uid = StringField('帐号', validators=[DataRequired()])
    pwd = PasswordField('密码', validators=[DataRequired()])
    tel = StringField('手机', validators=[DataRequired()])
    email = StringField('邮箱')
    submit = SubmitField('确定')
