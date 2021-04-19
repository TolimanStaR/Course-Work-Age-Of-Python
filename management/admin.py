from django.contrib import admin

from .models import AbstractTask, CodeFile, Test, Solution


@admin.register(AbstractTask)
class AbstractTaskAdmin(admin.ModelAdmin):
    search_fields = ('title',)


@admin.register(CodeFile)
class CodeFileAdmin(admin.ModelAdmin):
    pass


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    pass


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    pass
