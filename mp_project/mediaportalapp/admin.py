from django.contrib import admin

from mediaportalapp.models import Category, Article, Comments, UserAccount

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category)
admin.site.register(Comments)
admin.site.register(Article, ArticleAdmin)
admin.site.register(UserAccount)
