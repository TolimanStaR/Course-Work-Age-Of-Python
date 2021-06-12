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


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseTask)
class CourseTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseSolution)
class CourseSolutionAdmin(admin.ModelAdmin):
    pass


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    pass


@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(ContestSolution)
class ContestSolutionAdmin(admin.ModelAdmin):
    pass

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass
