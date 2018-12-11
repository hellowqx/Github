from django.contrib import admin

# Register your models here.

from .models import User,Article



class UserAdmin(admin.ModelAdmin):
    # # 修改 BooleanField 类型的内容展示
    # def is_delete_label(self):
    #     if self.is_delete:
    #         return "删除"
    #
    #     else:
    #         return "不删除"
    #     # 用于表头展示
    #
    # is_delete_label.short_description = "是否删除"

    list_display = ['id','name','nickname','age','sex','email','phone']
    #过滤器
    list_filter = ['age','sex']
    list_pet_page = 5
    #选择修改的选项
    fields = ['name','nickname','email']





actions_on_bottom = True
actions_on_top = False
admin.site.register(User,UserAdmin)
admin.site.register(Article)

search_fields = ["name", "nickname"]
#ordering 设置默认排序字段，负号表示降序排序
ordering = ('-publishTime',)

