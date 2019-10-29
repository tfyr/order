from django.db import models

# Create your models here.
from django.conf import settings
from datetime import datetime, date
from django.contrib.auth.models import User
from product.models import Item

DEFAULT_STATUS = 1
DEFAULT_ITEMSTATUS = 1

MEASURE_CHOICES = (
    (0, u'гр.'),
    (1, u'мл.'),
)

'''
class Item(models.Model):
    class Meta:
        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"
    name = models.CharField(verbose_name="Наименование", max_length=250)
    #category = models.ForeignKey(Category, verbose_name="Категория", null=False, blank=True, default=None, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(verbose_name="Вес", default=None, blank=True, null=True)
    measure = models.PositiveIntegerField('Ед. измерения', default=0, blank=False, null=False, choices=MEASURE_CHOICES)
    descr = models.CharField(verbose_name="Описание", max_length=5250)
    sostav = models.CharField(verbose_name="Состав", max_length=5250)
    price = models.PositiveIntegerField(verbose_name="Цена", default=None, blank=True, null=True)
    oldprice = models.PositiveIntegerField(verbose_name="Перечеркнутая цена", default=None, blank=True, null=True)

    #img180 = ResizedImageField(null=True, blank=True, size=[180, 120], quality=100, upload_to='')
    #img360 = ResizedImageField(null=True, blank=True, size=[360, 240], quality=100, upload_to='')
    #img720 = ResizedImageField(null=True, blank=True, size=[720, 480], quality=100, upload_to='')
    href = models.CharField(verbose_name="код для ссылки", max_length=64, unique=True, null=False, blank=False)
    #label = models.ManyToManyField(Label)


    def __str__(self):
        return str(self.name)
'''


class Status(models.Model): # Статус заказа
    status_text = models.CharField(max_length=50, unique=True)

    def __unicode__ (self):              # __unicode__ on Python 2
        return self.status_text
    def __str__(self):
        return self.status_text

    class Meta:
        #ordering = ['name']
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

class ItemStatus(models.Model): # Статус позиции заказа
    name = models.CharField('Наименование', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        #ordering = ['name']
        verbose_name = "Статус позиции заказа"
        verbose_name_plural = "Статусы позиций заказа"

def nvl(s):
    return '' if s is None else str(s)


PAY_CHOICES = (
    (0, u'Наличные'),
    (1, u'Карта'),
)
DELIVERY_CHOICES = (
    (0, u'Доставка'),
    (1, u'Самовывоз'),
)

class Order(models.Model):
    status = models.ForeignKey(Status, default=DEFAULT_STATUS, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField('Имя', max_length=250, default=None, null=True, blank=True)
    phone = models.CharField('Телефон', max_length=40, default=None, null=True, blank=True)
    email = models.CharField('E-mail', max_length=240, default=None, null=True, blank=True)
    street = models.CharField('Улица', max_length=250, default=None, null=True, blank=True)
    building = models.CharField('Дом', max_length=25, default=None, null=True, blank=True)
    flat = models.CharField('Квартира', max_length=20, default=None, null=True, blank=True)
    descr = models.CharField('Примечание', max_length=1255, default=None, null=True, blank=True)
    #delivery_date = models.DateField('Доставка', default=date.today)
    #delivery_period = models.CharField('Время доставки', max_length=10, default=None, null=True, blank=True)
    orderdate = models.DateTimeField('Дата и время поступления заказа', default= datetime.now)
    delivery_type = models.PositiveSmallIntegerField('Тип доставки', default=0, choices=DELIVERY_CHOICES)
    pay_type = models.PositiveSmallIntegerField('Тип оплаты', default=0, null=False, choices=PAY_CHOICES)
    cnt = models.IntegerField(verbose_name="Кол-во позиций", default=0)
    summa = models.DecimalField(verbose_name="Сумма заказа", default=0, max_digits=11, decimal_places=2)
    delivery_date = models.DateField('Доставка', default=None, null=True, blank=True)
    delivery_period = models.CharField('Время доставки', max_length=20, default=None, null=True, blank=True)

    def __str__(self):
        return u'Дата заказа: ' + str(self.orderdate) + \
               u', ' + nvl(self.name) + \
               u', тел: ' + nvl(self.phone) + \
               u', адрес: ' + nvl(self.street) + \
               u', д.' + nvl(self.building) + \
               u', кв.' + nvl(self.flat)

        #u', сумма: ' + str(self.price) + \
        # u', дата доставки: ' + str(self.delivery_date) + \

    class Meta:
        #ordering = ['name']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class ItemOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    cnt = models.IntegerField(verbose_name="Кол-во", default=1)
    price = models.DecimalField(verbose_name="Цена", default=0, max_digits=11, decimal_places=2)
    summa = models.DecimalField(verbose_name="Сумма", default=0, max_digits=11, decimal_places=2)
    status = models.ForeignKey(ItemStatus, default=DEFAULT_ITEMSTATUS, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return u'' + self.item.name + u', цена: ' + str(self.price) + u' руб., кол-во: ' + str(self.cnt) + u' шт,' + u', сумма: ' + str(self.summa) + u' руб.'

    def save(self, *args, **kwargs):
        self.summa = self.cnt * self.price
        super(ItemOrder, self).save(*args, **kwargs)


from django.db.models.signals import post_save
from django.dispatch import receiver

#@receiver(post_save, sender=ItemOrder)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=ItemOrder)
def save_user_profile(sender, instance, **kwargs):
    cnt=0
    sum=0
    for item in instance.order.items.all():
        if item.status_id!=2:
            cnt = cnt + item.cnt
            sum = sum + (item.cnt * item.price)
    instance.order.cnt=cnt
    instance.order.summa=sum
    instance.order.save()


