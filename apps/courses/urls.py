# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from .views import CourseListView, CourseDetailView, CourseCaptherView, CourseCOmmentView, AddCommentView, VideoPlayView

urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseListView.as_view(), name='course_list'),
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    url(r'^capther/(?P<course_id>\d+)/$', CourseCaptherView.as_view(), name='course_capther'),
    url(r'^comment/(?P<course_id>\d+)/$', CourseCOmmentView.as_view(), name='course_comment'),
    url(r'^addcomment/$', AddCommentView.as_view(), name='course_addcomment'),
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name='video_play'),

]
