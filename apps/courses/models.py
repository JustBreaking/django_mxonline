# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from future.utils import python_2_unicode_compatible
from organization.models import CourseOrg, Teacher

from DjangoUeditor.models import UEditorField


@python_2_unicode_compatible
class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name=u'课程机构', null=True)
    name = models.CharField(max_length=50, verbose_name=u'课程名' )
    desc = models.CharField(max_length=256, verbose_name=u'课程描述')
    teacher = models.ForeignKey(Teacher, max_length=50, verbose_name=u'讲师', null=True, blank=True )
    # detail = models.TextField(verbose_name=u'课程详情')
    detail = UEditorField(verbose_name=u'课程详情',width=600, height=300, toolbars="full",
            imagePath="courses/ueditor/",
            filePath="courses/ueditor/",
            default = ""
        )
    is_banner = models.BooleanField(verbose_name=u'是否轮播',default=False)
    degree = models.CharField(verbose_name=u'难度', max_length=2, choices=(('cj',u'初级'),('zj',u'中级'),('gj',u'高级')))
    learn_time = models.IntegerField(default=0, verbose_name=u'学习时长（分钟数）')
    students = models.IntegerField(default=0, verbose_name=u'学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏人数')
    image = models.ImageField(upload_to='courses/%Y/%m', verbose_name=u'封面图', max_length=64)
    click_nums = models.IntegerField(default=0, verbose_name=u'点击量')
    category = models.CharField(max_length=32, verbose_name=u'课程类别', default='django')
    tag = models.CharField(max_length=32, verbose_name=u'课程标签', default='')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    need_know = models.CharField(max_length=256, verbose_name=u'课程须知', default='')
    learn_what = models.CharField(max_length=256, verbose_name=u'能学到什么', default='')
    notice = models.CharField(max_length=64, verbose_name=u'课程公告', default='')

    class Meta:
        verbose_name = u'课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    #获取课程的章节数,可以和字段一样被注册到admin中
    def get_lesson_num(self):
        return self.lesson_set.all().count()
    get_lesson_num.short_description = u'章节数'
    #显示自定义的html
    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://baidu.com'>go</a>")
    go_to.short_description = "跳转"

    #获取学习该课程的用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    #获取课程所有章节
    def get_course_lesson(self):
        return self.lesson_set.all()

#用于后台展示时，轮播课程和普通课程分开，proxy参数置为false，并不会生成新的数据表
class CourseBanner(Course):
    class Meta:
        verbose_name = u'轮播课程'
        verbose_name_plural = verbose_name
        #必须设置为true，否则生成两张表
        proxy = True

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
        #获取章节视频
    def get_lesson_video(self):
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u'章节')
    url = models.URLField(max_length=128, verbose_name=u'访问地址', default='')
    name = models.CharField(max_length=64, verbose_name=u'视频名称')
    video_time = models.IntegerField(default=0, verbose_name=u'视频时长（分钟数）')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u'课程')
    name = models.CharField(max_length=64, verbose_name=u'名称')
    download = models.FileField(upload_to='course/resource/%Y%m', verbose_name=u'资源文件', max_length=64)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
