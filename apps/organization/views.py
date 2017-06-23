# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, redirect
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from .models import CourseOrg, CityDict
from operation.models import UserFavorite
from .forms import UserAskForm


class OrgView(View):
    def get(self, request):
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        all_citys = CityDict.objects.all()

        #取出筛选城市
        city_id = request.GET.get('city','')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #机构类别筛选
        category = request.GET.get('category','')
        if category:
            all_orgs = all_orgs.filter(category=category)

        #排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'course_nums':
                all_orgs = all_orgs.order_by('-course_nums')

        org_nums = all_orgs.count()

        #对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request) #每一页5条
        orgs = p.page(page)
        return render(request, 'org-list.html', {
                'all_orgs':orgs,
                'all_citys':all_citys,
                'org_nums':org_nums,
                'city_id':city_id,
                'category':category,
                'hot_orgs':hot_orgs,
                'sort':sort,
            })


class AddUserAskView(View):
    def post(relf, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)   #UserAskForm为一个ModelForm类，相较于Form类，它可以直接提交表单数据到数据库
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"提交出错"}', content_type='application/json')


#机构首页
class OrgHomeView(View):
    def get(self,request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:3]
        return render(request, 'org-detail-homepage.html',{
            'all_courses':all_courses,
            'all_teachers':all_teachers,
            'current_page':current_page,
            'course_org':course_org,
            'has_fav':has_fav,
        })

#机构课程列表页
class OrgCourseView(View):
    def get(self,request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html',{
            'all_courses':all_courses,
            'current_page':current_page,
            'course_org':course_org,
            'has_fav':has_fav,
        })


#机构课程列表页
class OrgDescView(View):
    def get(self,request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html',{
            'current_page':current_page,
            'course_org':course_org,
            'has_fav':has_fav,
        })


#机构讲师
class OrgTeacherView(View):
    def get(self,request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html',{
            'current_page':current_page,
            'course_org':course_org,
            'all_teachers':all_teachers,
            'has_fav':has_fav
        })

#用户收藏/取消收藏
class AddFavView(View):
    def post(self, request):
        fav_id = request.POST.get('fav_id',0)
        fav_type = request.POST.get('fav_type','')
        #判断是否登录
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        #若记录已经存在，则表示用户取消收藏
        if exist_records:
            exist_records.delete()
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')