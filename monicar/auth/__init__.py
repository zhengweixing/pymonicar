__author__ = 'zwx'
from flask import Blueprint

auth = Blueprint('auth', __name__)


from . import views