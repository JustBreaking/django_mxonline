# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from future.utils import python_2_unicode_compatible
from organization.models import CourseOrg


@python_2_unicode_compatible
class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name=u'课程机构', null=True)
    name = models.CharField(max_length=50, verbose_name=u'课程名' )
    desc = models.CharField(max_length=256, verbose_name=u'课程描述')
    detail = models.TextField(verbose_name=u'课程详情')
    degree = models.CharField(verbose_name=u'难度', max_length=2, choices=(('cj',u'初级'),('zj',u'中级'),('gj',u'高级')))
    learn_time = models.IntegerField(default=0, verbose_name=u'学习时长（分钟数）')
    students = models.IntegerField(default=0, verbose_name=u'学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏人数')
    image = models.ImageField(upload_to='courses/%Y/%m', verbose_name=u'封面图', max_length=64)
    click_nums = models.IntegerField(default=0, verbose_name=u'点击量')
    category = models.CharField(max_length=32, verbose_name=u'课程类别', default='django')
    tag = models.CharField(max_length=32, verbose_name=u'课程标签', default='')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    #获取课程的章节数
    def get_lesson_num(self):
        return self.lesson_set.all().count()

    #获取学习该课程的用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

@python_2_unicode_compatible
class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u'课程')
    name = models.CharField(max_length=64, verbose_name=u'章节名称')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u'章节')
    name = models.CharField(max_length=64, verbose_name=u'视频名称')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'视频'
        verbose_name_plural = verbose_name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u'课程')
    name = models.CharField(max_length=64, verbose_name=u'名称')
    download = models.FileField(upload_to='course/resource/%Y%m', verbose_name=u'资源文件', max_length=64)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程资源'
        verbose_name_plural = verbose_name
