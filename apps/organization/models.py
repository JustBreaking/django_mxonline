# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from future.utils import python_2_unicode_compatible

from DjangoUeditor.models import UEditorField


@python_2_unicode_compatible
class CityDict(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'城市')
    desc = models.TextField(verbose_name=u'描述')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'城市'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CourseOrg(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'机构名称')
    # desc = models.TextField(verbose_name=u'机构描述')
    desc = UEditorField(verbose_name=u'机构描述',width=600, height=300, toolbars="full",
            imagePath="org/ueditor/",
            filePath="org/ueditor/",
            default = ""
        )
    category = models.CharField(max_length=16, verbose_name=u'机构类别',choices=(('pxjg','培训机构'),('gr','个人'),('gx','高校')), default='pxjg')
    tag = models.CharField(max_length=10, verbose_name=u'机构标签', default=u'全国知名')
    click_nums = models.IntegerField(default=0, verbose_name=u'点击数')
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏数')
    image = models.ImageField(upload_to='org/%Y%m', verbose_name=u'logo')
    address = models.CharField(max_length=128, verbose_name=u'机构地址')
    city = models.ForeignKey(CityDict, verbose_name=u'所在城市')
    students = models.IntegerField(default=0, verbose_name=u'学习人数')
    course_nums = models.IntegerField(default=0, verbose_name=u'课程数')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程机构'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
    #获取机构下面的讲师数量
    def get_teacher_num(self):
        return self.teacher_set.all().count()


@python_2_unicode_compatible
class Teacher(models.Model):
    org = models.ForeignKey(CourseOrg, verbose_name=u'所属机构')
    name = models.CharField(max_length=64, verbose_name=u'教师名称')
    age = models.IntegerField(default=0, verbose_name=u'年龄')
    image = models.ImageField(upload_to='teacher/%Y%m', verbose_name=u'头像', default='teacher/default.png')
    work_years = models.IntegerField(default=0, verbose_name=u'工作年限')
    work_company = models.CharField(max_length=32, verbose_name=u'就职公司')
    work_position = models.CharField(max_length=32, verbose_name=u'公司职位')
    points = models.CharField(max_length=64, verbose_name=u'就学特点')
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏人数')
    click_nums = models.IntegerField(default=0, verbose_name=u'点击量')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'教师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_course_nums(self):
        return self.course_set.all().count()
