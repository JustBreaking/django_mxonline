# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponse

from .models import UserProfile, EmailVerfyRecord
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from utils.email_send import send_email_verification_code

#自定义可登录的字段，这里可以通过邮箱登录
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

def log_in(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, "index.html", {})
        else:
            return render(request, "login.html", {'msg':'用户名或密码错误'})
    elif request.method == 'GET':
        return render(request, "login.html", {})

#关于该类中get/POST的调用，是django自己完成的。
class LoginView(View):
    def get(self, request):
        login_form = LoginForm()
        return render(request, "login.html", {'login_form':login_form})
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")

            if UserProfile.objects.filter(username=username) is None:
                 return render(request, "login.html", {'msg':'用户未注册'})

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, "index.html")
                else:
                    return render(request, "login.html", {'msg':'用户未激活'})
            else:
                return render(request, "login.html", {'msg':'用户名或密码错误'})
        else:
            return render(request, "login.html", {'login_form':login_form})

class LogoutView(View):
    def get(self, request):
        url = request.POST.get('source_url', '/login')
        logout(request)
        return redirect(url)

# def log_out(request):
#     url = request.POST.get('source_url', '/login')
#     logout(request)
#     return redirect(url)


class ActiveUserView(View):
    def get(self, request, active_code):
        all_record = EmailVerfyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html',{'register_form':register_form})
    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = request.POST.get("email", "")
            if UserProfile.objects.filter(email=username):
                return render(request, 'register.html', {'register_form':register_form, 'msg':'用户已存在'})
            password1 = request.POST.get("password1", "")
            password2 = request.POST.get("password2", "")
            if password1 != password2:
                return render(request, 'register.html', {'register_form':register_form, 'msg':'密码输入不一致'})

            user = UserProfile()
            user.username = username
            user.email = username
            user.password = make_password(password1)
            user.is_active = False
            user.save()

            send_email_verification_code(username, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_form':register_form})

class ForgetPwdView(View):
    def get(self, request):
        forgetform = ForgetForm()
        return render(request, 'forgetpwd.html', {'forgetform':forgetform})
    def post(self, request):
        forgetform = ForgetForm(request.POST)
        if forgetform.is_valid():
            email = request.POST.get('email','')
            send_email_verification_code(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forgetform':forgetform})

class ResetPwdView(View):
    def get(self, request, reset_code):
        all_record = EmailVerfyRecord.objects.filter(code=reset_code)
        if all_record:
            for record in all_record:
                email = record.email
                if record.is_available:
                    record.is_available = False #访问验证链接之后将其设置为不再可用
                    record.save()
                    return render(request, "password_reset.html",{'email':email})
                else:
                    return HttpResponse('链接已过期')
        else:
            return HttpResponse('链接不存在')

    #注意：因为这里的url中带了reset_code参数，而post方法中并不会携带这个参数，所以这里不能定义post方法
    # def post(self, request):

class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            email = request.POST.get('email')
            if pwd1 != pwd2:
                return render(request, "password_reset.html",{'email':email, 'msg':'密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return HttpResponseRedirect('/login')
        else:
            email = request.POST.get('email')
            return render(request, "password_reset.html",{'email':email, 'modify_form':'modify_form'})
