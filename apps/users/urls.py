# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from .views import UserInfoView, UploadImageView, UpdatePwdView, SendEmailCodeView, UpdateEmailView, MyCourseView
from .views import MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessageView, MessageDetailView

urlpatterns = [
    #课用户信息
    url(r'^info/$', UserInfoView.as_view(), name='user_info'),

    #用户头像修改
    url(r'^image/upload/$', UploadImageView.as_view(), name='image_upload'),

    #用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),

    #个人中心修改邮箱，发送验证码
    url(r'^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),

    #修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    #我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),

    #我的收藏 包括课程、机构和讲师
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name='myfav_org'),
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name='myfav_course'),

    #我的消息-个人中心
    url(r'^mymessage/$', MyMessageView.as_view(), name='mymessage'),
    #点击消息后将消息置为已读并跳转到消息正文
    url(r'^message_detail/(?P<message_id>\d+)/$', MessageDetailView.as_view(), name='message_detail'),
]
