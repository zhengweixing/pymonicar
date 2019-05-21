from . import admin
from flask import redirect,url_for,request,render_template,abort
from flask_login import current_user


@admin.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('admin_base.html', title='-管理中心')