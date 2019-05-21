import hashlib,uuid
from flask_login import UserMixin
from . import db, login_manager


class Permission:
    ADD_STUDENT = 0x01
    START_STUDENT = 0x2
    PAY_STUDENT = 0x4
    MGR_STUDNET = 0x8
    ADMIN = 0x80


class Role(db.Model):
    __tablename__ = 'pre_ucenter_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            '学员组': (Permission.ADD_STUDENT,True),
            '驾校/教练': (Permission.ADD_STUDENT | Permission.START_STUDENT , False),
            '管理组': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'pre_ucenter_members'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('pre_ucenter_roles.id'))
    password = db.Column(db.String(128))
    gzwechatid = db.Column(db.String(64))
    qywechatid = db.Column(db.String(64))
    salt = db.Column(db.String(6))
    price = db.Column(db.Integer)
    email = db.Column(db.String(64))
    phone = db.Column(db.String(11))
    students = db.relationship('Student', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
            return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def can_add_stu(self):
        return self.can(Permission.ADD_STUDENT)

    def can_start_stu(self):
        return self.can(Permission.START_STUDENT)

    def get_id(self):
        return str(self.uid)

    @staticmethod
    def generate_token():
        return str(uuid.uuid1())

    def verify_password(self, password):
        password = hashlib.md5(password.encode('utf-8')).hexdigest() + self.salt
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        return self.password == password

    def set_password(self, password):
        self.salt = User.generate_token()[:6]
        password = hashlib.md5(password.encode('utf-8')).hexdigest() + self.salt
        self.password = hashlib.md5(password.encode('utf-8')).hexdigest()

    def get_students(self, is_complete=None, is_pay=None):
        if self.is_admin():
            if is_complete is not None:
                if not is_complete:
                    return Student.query.filter(Student.is_complete==is_complete, Student.is_pay>0).order_by(Student.id.desc())
                else:
                    return Student.query.filter_by(is_complete=is_complete).order_by(Student.id.desc())
            elif isinstance(is_pay, int):
                return Student.query.filter_by(is_pay=is_pay).order_by(Student.id.desc())
        else:
            if is_complete is not None:
                if not is_complete:
                    return self.students.filter(Student.is_complete==is_complete, Student.is_pay>0).order_by(Student.id.desc())
                else:
                    return self.students.filter_by(is_complete=is_complete).order_by(Student.id.desc())
            elif isinstance(is_pay, int):
                return self.students.filter_by(is_pay=is_pay).order_by(Student.id.desc())


class Student(db.Model):
    __tablename__ = 'pre_student_members'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(16))
    whoadd = db.Column(db.Integer, db.ForeignKey('pre_ucenter_members.uid'))
    totaltime = db.Column(db.Integer)
    flashIndex = db.Column(db.Integer)
    tel = db.Column(db.String(50))
    School = db.Column(db.String(100))
    email = db.Column(db.String(64))
    car_type = db.Column(db.String(50))
    is_login = db.Column(db.Boolean)
    is_run = db.Column(db.Boolean)
    time = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    is_complete_four = db.Column(db.Boolean)
    complete_time = db.Column(db.String(50))
    is_complete = db.Column(db.Boolean)
    is_pay = db.Column(db.Integer)
    citycode = db.Column(db.String(50))


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
    if user_id is not None and isinstance(user_id, int):
        return User.query.get(int(user_id))
    else:
        return None



"""
from monicar import db
db.create_all()
from  monicar.models import Role
admin = Role(name='Admin')
vip = Role(name='VIP')
db.session.add(admin)
db.session.add(vip)
from  monicar.models import User
user = User(username='admin', role=admin)
db.session.add(user)
db.session.commit()
"""


