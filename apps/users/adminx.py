#-*-coding:utf-8-*-
import xadmin
from xadmin import views
from xadmin.plugins.auth import UserAdmin

from .models import EmailVerfyRecord, Banner

#添加主题功能
class BaseSetting(object):
    #主题功能
    enable_themes = True
    use_bootswatch = True

#修改后台标题和页脚
class GlobalSettings(object):
    site_title = "暮雪后台管理系统"
    site_footer = "暮雪在线网"
    menu_style = 'accordion'    #隐藏每个app下面的models


class EmailVerfyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    #自定义的搜索字段
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
    model_icon = 'fa fa-envelope-o'

class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerfyRecord,EmailVerfyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
