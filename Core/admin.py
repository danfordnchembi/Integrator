from django.contrib import admin
from . import views
from .models import Query


# Register your models here.
class QueryAdmin(admin.ModelAdmin):
    list_display = ["message_type", "sql_statement", "condition_field"]



admin.site.register(Query, QueryAdmin)