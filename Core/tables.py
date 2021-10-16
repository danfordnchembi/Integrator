import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.html import escape
import itertools
from Core import models as core_models


class Actions(tables.Column):
    empty_values = list()

    def render(self, value, record):
        return mark_safe('<button id="%s" class="btn_delete btn btn-danger'
                         ' btn-sm"><i class="la la-trash"></i>Delete</button> '
                         '<button id="%s" class="btn_update btn btn-primary'
                         ' btn-sm"><i class="la la-pencil"></i>Edit</button> '
                         % (escape(record.id),escape(record.id)))


class CPTCodeMappingTable(tables.Table):
    Actions = Actions()
    counter = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = core_models.CPTCodesMapping
        template_name = "django_tables2/bootstrap.html"
        fields = ('counter','cpt_code__code', 'cpt_code__description','local_code')
        row_attrs = {
            'data-id': lambda record: record.pk
        }

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter',
                                   itertools.count(self.page.start_index()))
        return next(self.row_counter)