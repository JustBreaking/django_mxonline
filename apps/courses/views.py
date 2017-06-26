# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, redirect
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComment, UserCourse
from utils.mixin_utils import LoginRequiredMixin


#课程列表页
class CourseListView(View):
    def get(self,request):
        all_courses = Course.objects.order_by("-add_time")

        hot_courses = Course.objects.order_by("-click_nums")[:3]

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords)) #Q or i 不区分大小写

        #排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        #对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 9, request=request) #每一页3条
        courses = p.page(page)
        return render(request, 'course-list.html', {
            'all_courses':courses,
            'sort':sort,
            'hot_courses':hot_courses,
        })


#课程详情页
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        course.click_nums += 1
        course.save()

        #相关课程推荐是通过查询和该课程 有相同tag的课程
        if course.tag:
            relate_courses = Course.objects.filter(tag=course.tag).exclude(id=int(course_id))[:3]
        else:
            relate_courses = []

        has_course_fav = False
        has_org_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_id), fav_type=1):
                has_course_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_org_fav = True

        return render(request, 'course-detail.html', {
            'course':course,
            'relate_courses':relate_courses,
            'has_course_fav':has_course_fav,
            'has_org_fav':has_org_fav,
        })


#课程章节信息
class CourseCaptherView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()

        all_resources = CourseResource.objects.filter(course=course)

        #查询用户是否关联了课程
        user_course0 = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course0:
            add_user_course = UserCourse(user=request.user, course=course)
            add_user_course.save()

        #课程推荐
        user_courses = UserCourse.objects.filter(course=course)
        #所有学过该课程的用户id
        user_ids = [user_course.user.id for user_course in user_courses]
        #所有学过该课程的用户，学习的所有课程
        #user_id UserCourse中user的外键是一个UserProfile
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出all_user_courses的课程id
        all_user_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        #取出相关课程中点击率前5的课程
        relate_courses = Course.objects.filter(id__in=all_user_courses_ids).order_by('-click_nums')[:5]


        return render(request, 'course-video.html',{
            'course':course,
            'all_resources':all_resources,
            'relate_courses':relate_courses,
        })


#课程评论
class CourseCOmmentView(LoginRequiredMixin, View):
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        all_comments = CourseComment.objects.filter(course=course)

        #课程推荐
        user_courses = UserCourse.objects.filter(course=course)
        #所有学过该课程的用户id
        user_ids = [user_course.user.id for user_course in user_courses]
        #所有学过该课程的用户，学习的所有课程
        #user_id UserCourse中user的外键是一个UserProfile
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出all_user_courses的课程id
        all_user_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        #取出相关课程中点击率前5的课程
        relate_courses = Course.objects.filter(id__in=all_user_courses_ids).order_by('-click_nums')[:5]

        return render(request, 'course-comment.html',{
            'course':course,
            'all_comments':all_comments,
            'relate_courses':relate_courses,
        })


class AddCommentView(View):
    def post(self,request):
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get('course_id',0) #参数名必须和ajax中的data中参数名一致
        comment = request.POST.get('comments', '')
        if course_id > 0 and comment:
            course_comment = CourseComment()
            course = Course.objects.get(id=int(course_id))
            course_comment.course = course
            course_comment.comments = comment
            course_comment.user = request.user
            course_comment.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')


class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComment.objects.filter(course=course)

        #课程推荐
        user_courses = UserCourse.objects.filter(course=course)
        #所有学过该课程的用户id
        user_ids = [user_course.user.id for user_course in user_courses]
        #所有学过该课程的用户，学习的所有课程
        #user_id UserCourse中user的外键是一个UserProfile
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出all_user_courses的课程id
        all_user_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        #取出相关课程中点击率前5的课程
        relate_courses = Course.objects.filter(id__in=all_user_courses_ids).order_by('-click_nums')[:5]


        return render(request, 'course-play.html',{
            'course':course,
            'all_comments':all_comments,
            'all_resources':all_resources,
            'relate_courses':relate_courses,
            'video':video,
        })
