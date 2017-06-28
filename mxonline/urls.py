# -*- coding: utf-8 -*-
"""mxonline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.views.static import serve

# from django.contrib import admin
import xadmin

# from users.views import log_in, log_out
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetPwdView, ModifyPwdView, LogoutView
import organization, courses, users
from users.views import IndexView
from mxonline.settings import MEDIA_ROOT


urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$', IndexView.as_view(), name="index"),
    # url(r'^login/$', log_in, name="login"),
    url(r'^login/$', LoginView.as_view(), name="login"), #基于类实现登陆
    url(r'^register/$', RegisterView.as_view(), name="register"), #基于类实现登陆
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>[a-zA-Z0-9]{16})/$', ActiveUserView.as_view(), name='active_user'),
    url(r'^forget/', ForgetPwdView.as_view(), name='forget'),   #forget password
    url(r'^reset/(?P<reset_code>[a-zA-Z0-9]{16})/$', ResetPwdView.as_view(), name='reset'), #reset password
    url(r'^modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    # url(r'^logout/$', log_out, name="logout"),

    #课程机构，讲师等url配置
    url(r'^org/', include('organization.urls', namespace='org')),
    #课程相关url配置
    url(r'^course/', include('courses.urls', namespace='course')),
    #用户相关url配置
    url(r'^users/', include('users.urls', namespace='users')),

    #富文本相关
    url(r'^ueditor/',include('DjangoUeditor.urls' )),

    #设置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT}),

    # url(r'^static/(?P<path>.*)$', serve, {"document_root":STATIC_ROOT}),
]

#全局404页面配置
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'
