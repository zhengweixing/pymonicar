from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class StudentForm(Form):
    uid = StringField('身份证帐号', validators=[DataRequired()])
    pwd = StringField('登录密码', validators=[DataRequired()])
    card_no = StringField('学习卡帐号')
    card_pwd = StringField('学习卡密码')
    xue_shi_type = SelectField('学习网站', coerce=int, choices=[(0, '悦驾网'), (1, '车尚网')])
    check_code = StringField('验证码')
    submit = SubmitField('提交')

    def clearn(self):
        self.uid.data = ''
        self.pwd.data = ''
        self.card_no.data = ''
        self.card_pwd.data = ''


class YuYueForm(Form):
    uid = StringField('身份证帐号', validators=[DataRequired()])
    pwd = StringField('登录密码', validators=[DataRequired()])
    check_code = StringField('验证码')
    submit = SubmitField('提交')