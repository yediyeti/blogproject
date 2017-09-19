#encoding=utf-8
from django.contrib import admin
from .models import Post, Category, Tag

# 定制admin后台
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    
# Register your models here.
# 将新增的PostAdmin的注册
admin.site.register(Post,PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)