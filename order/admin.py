from django.contrib import admin

# Register your models here.
from django.db.models import Count, Sum

from order.models import Order, ItemOrder, Status, ItemStatus


class ItemOrderInline(admin.TabularInline):
    model = ItemOrder

    fields = ['item', 'cnt', 'price', 'summa', 'status']
    readonly_fields = ['summa', ]
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

    fields = ['customer', 'status', 'name', 'phone', 'email', 'street', 'building', 'flat', 'descr', 'orderdate', 'delivery_date', 'delivery_period',  'delivery_type', 'pay_type', 'cnt', 'summa', ]

    list_filter = [
        'status',
    ]


    search_fields = ['name', 'sostav', ]
    readonly_fields = ('customer', 'cnt', 'summa', )
    inlines = [ItemOrderInline]


admin.site.register(Status)
admin.site.register(ItemStatus)
admin.site.register(Order, OrderAdmin)
