# -*- coding: utf-8 -*-

import re

from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm):
    #my_field = forms.CharField()   #可以新增model没有的字段
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']
    #对mobile字段进行自定义验证
    def clean_mobile(self):
        #验证手机号码是否合法
        mobile = self.cleaned_data['mobile']
        regix_mobile = '^1(3[0-9]|4[57]|5[0-35-9]|7[0135678]|8[0-9])\d{8}$'
        p = re.compile(regix_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u'手机号码不合法',code='mobile_invalid')
