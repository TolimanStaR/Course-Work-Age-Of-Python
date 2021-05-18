from django.contrib import admin

from .models import *


class CoursesInLine(admin.StackedInline):
    model = Course


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    inlines = [CoursesInLine, ]


class BlockContentInLine(admin.StackedInline):
    model = CourseDescriptionBlock


class ModuleInLine(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [BlockContentInLine, ModuleInLine, ]


class ListElementInLine(admin.StackedInline):
    model = ModuleDescriptionListElement


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [ListElementInLine, ]
