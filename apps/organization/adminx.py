# -*- coding: utf-8 -*-

import xadmin
from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name','desc','add_time']
    search_fields = ['name','desc']
    list_filter = ['name','desc','add_time']

class CourseOrgAdmin(object):
    list_display = ['name','desc','category','click_nums','fav_nums','image','address','city','add_time']
    #search_fields 和 list_filter 中，city为该表的外键，通过它搜索时，必须指明是外键的哪一个字段
    search_fields = ['name','desc','category','click_nums','fav_nums','image','address','city__name']
    list_filter = ['name','desc','category','click_nums','fav_nums','image','address','city__name','add_time']

    style_fields = {'desc':'ueditor'}

class TeacherAdmin(object):
    list_display = ['org','name','work_years','work_company','work_position','points','fav_nums','click_nums','add_time']
    search_fields = ['org__name','name','work_years','work_company','work_position','points','fav_nums','click_nums']
    list_filter = ['org__name','name','work_years','work_company','work_position','points','fav_nums','click_nums','add_time']

xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
