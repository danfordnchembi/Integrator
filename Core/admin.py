from django.contrib import admin
from . import views
from .models import Query, PayloadConfig


# Register your models here.
class QueryAdmin(admin.ModelAdmin):
    list_display = ["message_type", "sql_statement", "condition_field"]


class PayloadConfigAdmin(admin.ModelAdmin):
    list_display = ["message_type", "chunk_size"]



admin.site.register(Query, QueryAdmin)
admin.site.register(PayloadConfig,PayloadConfigAdmin)