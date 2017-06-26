# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import update_session_auth_hash

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import UserProfile, EmailVerfyRecord
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_email_verification_code
from utils.mixin_utils import LoginRequiredMixin

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
    if request.user.is_authenticated:
        return redirect('/')
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
        #已登录的用户直接跳转到首页
        if request.user.is_authenticated():
            return redirect('/')

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

            #注册成功后写入消息
            user_message = UserMessage()
            user_message.user = user.id
            user_message.message = "欢迎注册暮雪在线！"
            user_message.has_read = False
            user_message.save()

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

#未登录状态忘记密码的修改密码
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


#用户个人信息
#继承 LoginRequiredMixin必须登录才能访问
class UserInfoView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'usercenter-info.html',{

        })
    def post(self, request):
        userinfo_form = UserInfoForm(request.POST, instance=request.user)
        if userinfo_form.is_valid():
            userinfo_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(userinfo_form.errors), content_type='application/json')


#用户头像修改
class UploadImageView(View):
    def post(self, request):
        #uploadimage_form是一个ModelForm，可以直接保存到数据库
        uploadimage_form = UploadImageForm(request.POST, request.FILES, instance=request.user)  #instance直接指明一个实例化对象
        if uploadimage_form.is_valid():
            uploadimage_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')

#个人中心修改密码
class UpdatePwdView(LoginRequiredMixin, View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            oldpassword = request.POST.get('oldpassword','')
            if not authenticate(username=request.user, password=oldpassword):
                return HttpResponse('{"status":"fail", "msg":"密码有误"}', content_type='application/json')

            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail", "msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd1)
            user.save()
            # update_session_auth_hash(request, user)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')

#发送邮箱验证码
class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"该邮箱已被注册"}', content_type='application/json')
        send_email_verification_code(email, "update")
        return HttpResponse('{"success":"验证码已发送至邮箱"}', content_type='application/json')

#修改个人中心邮箱
class UpdateEmailView(View):
    def post(self, request):
        email = request.POST.get('email','')
        code = request.POST.get('code','')

        existed_records = EmailVerfyRecord.objects.filter(email=email, code=code, send_type='update', is_available = True)
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            #更改邮箱后将验证码置为无效
            for existed_record in existed_records:
                existed_record.is_available = False
                existed_record.save()

            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码有误"}', content_type='application/json')

class MyCourseView(LoginRequiredMixin, View):
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html",{
            'user_courses':user_courses,
        })


class MyFavOrgView(View):
    def get(self, request):
        org_list = []
        user_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for user_org in user_orgs:
            org_id = user_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html",{
            'org_list':org_list,
        })

class MyFavTeacherView(View):
    def get(self, request):
        teacher_list = []
        user_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for user_teacher in user_teachers:
            teacher_id = user_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "usercenter-fav-teacher.html",{
            'teacher_list':teacher_list,
        })

class MyFavCourseView(View):
    def get(self, request):
        course_list = []
        user_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for user_course in user_courses:
            course_id = user_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, "usercenter-fav-course.html",{
            'course_list':course_list,
        })

class MyMessageView(View):
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        #对消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 5, request=request) #每一页5条
        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            'messages':messages,
        })

#个人中心消息详情页，点击之后将其置为已读
class MessageDetailView(View):
    def get(self, request, message_id):
        message = UserMessage.objects.get(id=message_id)
        message.has_read = True
        message.save()
        return render(request, 'usercenter-message-detail.html', {
            'message':message,
        })
