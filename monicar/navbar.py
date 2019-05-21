from flask_nav.elements import *
from . import nav

# registers the "top" menubar
nav.register_element('top', Navbar(
    View('学时系统', 'main.index'),
    View('首页', 'main.index'),
    View('新增学员', 'main.add_stu'),
    Subgroup(
        '学员管理',
        View('未完成', 'main.mgr_stu', act='weiwancheng'),
        View('已完成', 'main.mgr_stu', act='yiwancheng'),
        View('未缴费', 'main.mgr_stu', act='weijiaofei'),
        View('后缴费', 'main.mgr_stu', act='houjiaofei'),
        View('已缴费', 'main.mgr_stu', act='yijiaofei')
    ),
    Subgroup(
        '相关网站',
        Link('科三预约','http://gd.122.gov.cn/'),
        Link('悦驾网','http://car.monicar.cn'),
        Link('车尚网', 'http://dgcheshang.cn/'),
        Link('车管所','http://www.dgjj.gov.cn/business/'),
        Link('阳光网投诉','http://wz.sun0769.com/index.php/question/reply'),
        Separator(),
        Link('旧系统', dest='http://ci.ashufa.com')
    ),
    View('教程', 'main.help'),
    View('登录/注册','auth.login')
))