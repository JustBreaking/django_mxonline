# -*- coding: utf-8 -*-

import xadmin
import xlrd
from .models import Course, Lesson, Video, CourseResource, CourseBanner
from organization.models import CourseOrg

class LessonInline(object):
    model = Lesson
    extra = 0

class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    #Course 中的方法 get_lesson_num 也可以放在展示列表中
    list_display = ['name','desc','detail','degree','learn_time','students','fav_nums','image','click_nums','get_lesson_num','go_to','add_time']
    search_fields = ['name','desc','detail','degree', 'students','fav_nums','image','click_nums']
    list_filter = ['name','desc','detail','degree','learn_time','students','fav_nums','image','click_nums','add_time']
    #根据点击排序
    ordering = ['-click_nums']
    #指定只读（不可修改）的字段
    readonly_fields = ['click_nums']
    #可直接在列表页编辑的字段
    list_editable = ['degree', 'desc']
    #指定在编辑状态不显示的字段
    exclude = ['fav_nums']
    #添加课程时，可以直接添加章节, Lesson 和 CourseResource 均有外键指向Course
    inlines = [LessonInline, CourseResourceInline]

    style_fields = {'detail':'ueditor'}

    #import_excel位True，excel导入,会覆盖插件中(plugins/excel.py)import_excel的默认值
    import_excel = True
    #将导入的excel文件内容存入数据库的course表中
    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['excel'].read())
            table = wb.sheets()[0]
            row = table.nrows
            sql_list = []
            org_id_list = []
            for i in xrange(1,row):
                col = table.row_values(i)
                sql = Course(
                    degree=col[0],
                    learn_time=col[1],
                    detail=col[2],
                    desc=col[3],
                    students=col[4],
                    fav_nums=col[5],
                    name=col[6],
                    image=col[7],
                    click_nums=col[8],
                    course_org_id=col[10],
                    category=col[11],
                    tag=col[12],
                    teacher_id=col[13],
                    learn_what=col[14],
                    need_know=col[15],
                    notice=col[16],
                    is_banner=col[17],
                )
                sql_list.append(sql)
                org_id_list.append(col[10])
            Course.objects.bulk_create(sql_list)

            #更新excel文件中机构包含的课程数
            for id in org_id_list:
                org = CourseOrg.objects.get(id=int(id))
                org_course_nums = org.course_set.all().count()
                org.course_nums = org_course_nums
                org.save()

        return super(CourseAdmin, self).post(request, args, kwargs)

    #页面定时刷新,在页面选择
    # refresh_times = [3,5]

    #页面展示的数据过滤（只展示符合条件的数据）
    def queryset(self):
        course_ = super(CourseAdmin, self).queryset()
        course_ = course_.filter(is_banner=False)
        return course_

    #保存课程时统计课程机构的课程数
    def save_models(self):
        obj = self.new_obj  #新建一个课程对象
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


#后台再注册一个轮播课程，和普通课程分开展示
class CourseBannerAdmin(CourseAdmin):
    #只需要是轮播图的课程
    def queryset(self):
        #将将 self(即CourseBannerAdmin) 转化为 CourseAdmin的父类(即object)，然后调用object的queryset()方法
        banner_course = super(CourseAdmin, self).queryset()
        banner_course = banner_course.filter(is_banner=True)
        return banner_course


class LessonAdmin(object):
    list_display = ['course','name','add_time']
    search_fields = ['course__name','name']
    list_filter = ['course__name','name','add_time']    #course为lesson的外键，通过 __name的方式指明通过外键course中的name进行搜索

class VideoAdmin(object):
    list_display = ['lesson','name','add_time']
    search_fields = ['lesson__name','name']
    list_filter = ['lesson__name','name','add_time']

class CourseResourceAdmin(object):
    list_display = ['course','name', 'download', 'add_time']
    search_fields = ['course__name','name', 'download']
    list_filter = ['course__name','name', 'download','add_time']

xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)

xadmin.site.register(CourseBanner, CourseBannerAdmin)
