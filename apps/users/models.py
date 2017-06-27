# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.utils.encoding import python_2_unicode_compatible
from future.utils import python_2_unicode_compatible

@python_2_unicode_compatible
#继承了AbstractUser,该类中已有user的很多信息
class UserProfile(AbstractUser):
    nickname = models.CharField(max_length=16, verbose_name=u'昵称', default="")
    birday = models.DateField(verbose_name=u'生日', null=True, blank=True)
    gender = models.CharField(max_length=8, choices=(('male',u'男'),('female',u'女')))
    address = models.CharField(max_length=64, default="")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to="image/%Y/%m", default = 'image/default.png', max_length=64)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name  #复数形式，若不设置，后台显示会多一个s

    def __str__(self):
        return self.username

    def get_unread_nums(self):
        from operation.models import UserMessage    #只能放在这里，否则会循环引用
        return UserMessage.objects.filter(user=self.id, has_read=False).count()


@python_2_unicode_compatible
class EmailVerfyRecord(models.Model):
    code = models.CharField(max_length=16, verbose_name=u'验证码')
    email = models.EmailField(max_length=32, verbose_name=u'邮箱')
    is_available = models.BooleanField(default=False, verbose_name=u'是否可用') #验证码是否可用
    send_type = models.CharField(verbose_name=u'验证码类型', max_length=16, choices=(('register',u'注册'),('forget',u'找回密码'),('update',u'修改邮箱')))
    send_time = models.DateTimeField(verbose_name=u'发送时间', default=datetime.now)  #now（）需要去掉括号，才会根据实例化的时间

    class Meta:
        verbose_name = u'邮箱验证码'
        verbose_name_plural = verbose_name
    #override
    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)

class Banner(models.Model):
    title = models.CharField(max_length=32, verbose_name=u'标题')
    image = models.ImageField(upload_to='banner/%Y/%m', verbose_name=u'轮播图')
    url = models.URLField(max_length=128, verbose_name=u'访问地址')
    index = models.IntegerField(default=100, verbose_name=u'顺序')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'轮播图'
        verbose_name_plural = verbose_name
