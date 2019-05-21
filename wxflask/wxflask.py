import traceback, six, time
from flask import request, abort
from wechatpy.enterprise import WeChatClient as QYWeChatClient
from wechatpy.client import WeChatClient as GZWeChatClient
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply
from wechatpy.messages import BaseMessage
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from . import from_gongzhong, from_qiye


def __get_key(self):
    key = 'default_hander'
    if self.type.lower() == 'event':
        if self.event.lower() in ['subscribe', 'unsubscribe', 'location', 'enter_agent', 'batch_job_result']:
            key = self.event
        elif self.event.lower() in ['click', 'scancode_push', 'scancode_waitmsg', 'pic_sysphoto', 'pic_photo_or_album', 'pic_weixin', 'location_select']:
            key = self.key
        elif self.event.lower() in ['view']:
            key = self.event
    elif self.type.lower() in ['shortvideo', 'text', 'image', 'voice', 'video', 'location', 'link']:
        key = self.type
    return key

BaseMessage.get_hand_key = __get_key


class Session(object):
    def __init__(self):
        self.__store = {}

    def get(self, key):
        now = time.time()
        if key in self.__store:
            value, expires = self.__store[key]
            if expires is not None and now > expires:
                self.__store.pop(key)
                return None
            else:
                return value
        else:
            return None

    def pop(self, key):
        now = time.time()
        if key in self.__store:
            value, expires = self.__store.pop(key)
            return None if expires is not None and now > expires else value
        else:
            return None

    def set(self,key, value, expires=None):
        if expires is None:
            expires = 3*60*60
        expires = expires + time.time()
        self.__store[key] = value,expires


class WXFlask:

    __hand_map = {}
    __before_hand = None
    __qy_wechat_client = None
    __gz_wechat_client = None
    __gzcrypto = None
    __crypto = None
    session = None

    def __init__(self, app=None):
        self.session = Session()
        if app is not None:
            self.init_app(app)
        else:
            self.app=None

    def client(self, type=None):
        if type == from_gongzhong:
            return self.__gz_wechat_client
        else:
            return self.__qy_wechat_client

    def init_app(self, app):
        self.app = app
        app.config.setdefault('WECHAT_QIYE_RULE', '/wechat/qy')
        app.config.setdefault('WECHAT_GONGZHONG_RULE', '/wechat/gz')
        self.__crypto = WeChatCrypto(app.config['STOKEN'],app.config['SENCODINGAESKEY'],app.config['SCORPID'])
        self.__gzcrypto = WeChatCrypto(app.config['STOKEN'], app.config['SENCODINGAESKEY'], app.config['APPID'])
        self.__bind_rule(app, methods=['GET', 'POST'])

        self.__qy_wechat_client = QYWeChatClient(app.config['SCORPID'], app.config['QI_YE_SECRET'], app.config['STOKEN'])
        self.__gz_wechat_client = GZWeChatClient(app.config['APPID'], app.config['FU_WU_HAO_SECRET'], app.config['STOKEN'])

    def __bind_rule(self, app, **options):
        endpoint = options.pop('endpoint', None)
        app.add_url_rule(self.app.config['WECHAT_QIYE_RULE'], endpoint, self.__qyhand__, **options)
        app.add_url_rule(self.app.config['WECHAT_GONGZHONG_RULE'], endpoint, self.__gzhand__, **options)

    def __gzhand__(self):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        encrypt_type = request.args.get('encrypt_type', 'raw')
        msg_signature = request.args.get('msg_signature', '')
        try:
            check_signature(self.app.config['STOKEN'], signature, timestamp, nonce)
        except InvalidSignatureException:
            abort(403)
        if request.method == 'GET':
            echo_str = request.args.get('echostr', '')
            return echo_str

        # POST request
        if encrypt_type == 'raw':
            # plaintext mode
            msg = parse_message(request.data)
            return self.__do(from_gongzhong, msg)
        else:
            try:
                msg = self.__gzcrypto.decrypt_message(
                    request.data,
                    msg_signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidAppIdException):
                abort(403)
            else:
                msg = parse_message(msg)
                reply = self.__do(from_gongzhong, msg)
                return self.__gzcrypto.encrypt_message(reply, nonce, timestamp)

    def __qyhand__(self):
        signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')

        if request.method == 'GET':
            echo_str = request.args.get('echostr', '')
            try:
                echo_str = self.__crypto.check_signature(
                    signature,
                    timestamp,
                    nonce,
                    echo_str
                )
            except InvalidSignatureException:
                return 'ERROR Invalid Signature!'
            return echo_str
        else:
            try:
                msg = self.__crypto.decrypt_message(
                    request.data,
                    signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidCorpIdException):
                return 'ERROR Invalid Signature!'
            msg = parse_message(msg)
            reply = self.__do(from_qiye, msg)
            res = self.__crypto.encrypt_message(reply, nonce, timestamp)
            return res

    def __do(self, where_from, msg):
        try:
            return  self.__hand_msg(where_from, msg)
        except Exception as e:
            error = traceback.format_exc()
            return create_reply(error, msg).render()

    def register(self, key):
        """消息事件的处理函数的注册"""
        def decorator(fun):
            self.__hand_map[key] = fun
            return fun
        return decorator

    def before_hand(self, callback):
        self.__before_hand = callback
        return callback

    def __hand_msg(self, where_from, msg):
        key = msg.get_hand_key()
        if self.__before_hand:
            result = self.__before_hand(where_from, msg)
            if result is not None and isinstance(result,six.string_types):
                return result
        if key in self.__hand_map.keys():
            fun = self.__hand_map[key]
        else:
            fun = self.__hand_map['default_hander']
        return fun(where_from, msg)
