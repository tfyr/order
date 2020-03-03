from django.contrib import admin

# Register your models here.
from django.db.models import Count, Sum

from order.models import Order, ItemOrder, Status, ItemStatus


class ItemOrderInline(admin.TabularInline):
    model = ItemOrder

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ItemOrderInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields['status'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False
        return formset

    fields = ['item', 'cnt', 'price', 'summa', 'status']
    readonly_fields = ['item', 'summa', ]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'orderdate',
        'customer',
        'phone',
        'name',
        'street',
        'building',
        'flat',
        'cnt',
        'summa',
        'delivery_date',
        'delivery_period',
        'status',
    )

    fields = [
        'customer',
        'status',
        ('name', 'phone', 'email',),
        ('street', 'building', 'flat',),
        'descr',
        'orderdate',
        'delivery_date', 'delivery_period',
        'delivery_type',
        'pay_type',
        'cnt',
        'summa',
    ]

    list_filter = [
        'status',
    ]


    search_fields = ['name', 'sostav', ]
    readonly_fields = ('customer', 'cnt', 'summa', )
    inlines = [ItemOrderInline]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(OrderAdmin, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields['status'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False
        return formset



admin.site.register(Status)
admin.site.register(ItemStatus)
admin.site.register(Order, OrderAdmin)
