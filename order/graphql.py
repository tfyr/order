import graphene
from graphene_django import DjangoObjectType
from nashcart.cart import Cart
from datetime import datetime

from promocodes.models import Promoused
from telegram.telegram import send_mess

from order.models import Order, ItemOrder, Status, ItemStatus, Item


class ItemType(DjangoObjectType):
    class Meta:
        model = Item


class StatusType(DjangoObjectType):
    class Meta:
        model = Status


class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class ItemOrderType(DjangoObjectType):
    class Meta:
        model = ItemOrder



class ItemStatusType(DjangoObjectType):
    class Meta:
        model = ItemStatus


class Query(object):
    order = graphene.Field(OrderType, id=graphene.Int(),)
    orders = graphene.List(OrderType, )
    itemorder = graphene.List(ItemOrderType)
    status = graphene.Field(StatusType, )
    itemstatus = graphene.Field(ItemStatusType, )

    def resolve_items(self, info, **kwargs):
        return Item.objects.all()


    def resolve_order(self, info, **kwargs):
        user = info.context.user
        if not user or user.is_anonymous: # no orders for anonymous
            return None
        id = kwargs.get('id')
        return Order.objects.get(pk=id, customer=user) # can read just their orders

    def resolve_orders(self, info, **kwargs):
        user = info.context.user
        if not user or user.is_anonymous: # no orders for anonymous
            return None
        return Order.objects.filter(customer=user).order_by('-id') # can read just their orders

    def resolve_itemorder(self, info, **kwargs):
        return ItemOrder.objects.all()

    def resolve_status(self, info, **kwargs):
        return Status.objects.all()


class OrderX(graphene.Mutation):
    ok = graphene.Boolean()
    order = graphene.Field(OrderType)
    #cart = graphene.List(CartType)
    #cart_summary = graphene.Field(CartSummaryType)

    class Arguments:
        name = graphene.String(required=True)
        phone = graphene.String(required=True)
        email = graphene.String(required=False)
        street = graphene.String(required=False)
        building = graphene.String(required=False)
        flat = graphene.String(required=False)
        descr = graphene.String(required=False)
        delivery_type = graphene.Int()
        pay_type = graphene.Int()
        #price = graphene.Decimal(required=True)
        deliverydate= graphene.String(required=False)
        deliveryperiod= graphene.String(required=False)

    @classmethod
    def mutate(cls, root, info, **args):

        cart = Cart(session=info.context.session)
        name = args.get('name')
        if name:
            name=name.strip()
        phone = args.get('phone')
        if phone:
            phone=phone.strip()
        email = args.get('email')
        if email:
            email=email.strip()
        street = args.get('street')
        if street:
            street=street.strip()
        building = args.get('building')
        if building:
            building=building.strip()
        flat = args.get('flat')
        if flat:
            flat=flat.strip()
        descr = args.get('descr')

        delivery_type = args.get('delivery_type')
        pay_type = args.get('pay_type')

        deliverydate = args.get('deliverydate')
        deliveryperiod = args.get('deliveryperiod')
        try:
            dd=datetime.strptime(deliverydate, '%d-%m-%Y')
        except:
            dd=None

        order = Order(
            name=name,
            phone=phone,
            email=email,
            street=street,
            building=building,
            flat=flat,
            descr=descr,
            customer=None if info.context.user.is_anonymous else info.context.user,
            delivery_type = delivery_type,
            pay_type=pay_type,
            delivery_date=dd,
            delivery_period = deliveryperiod,
        )

        order.save()
        tlg_items=''
        total_price=0
        for itemcart in cart:
            if itemcart.quantity < 1:
                continue
            #order.price = order.price + itemcart.total_price
            item=Item.objects.get(pk=itemcart.object_id)
            itemorder = ItemOrder(
                order=order,
                item=item,
                cnt=itemcart.quantity,
                price=itemcart.total_price/itemcart.quantity,
                summa=itemcart.total_price)
            tlg_items+="{} x {} = {} ₽\n".format(item.name, itemcart.quantity, itemcart.total_price)
            total_price+=itemcart.total_price
            itemorder.save()

        promos=""
        promoselected=Promoused.objects.filter(cart_id=cart.cart.id)
        for promo in promoselected:
            promos += promo.code.code + ", "
        promoselected.delete()
        msg = u"Заказ #{}\nИмя: {}\nТел: {}\nEmail: {}\nДата доставки: {}\n{}\n{}Примечание: {}\n\n{}\nИтого: {} ₽"\
            .format(order.id, name, phone, email, dd.strftime("%d.%m.%Y") if dd else "", "Ул. {}, д. {}, кв. {}".format(street, building, flat) if delivery_type==0 else "Самовывоз",
                    "" if not promos else "Промокоды: {}\n".format(promos),
                    descr, tlg_items, total_price)

        #chat_id = get_chat_id(last_update(get_updates_json(url)))
        #send_mess(chat_id, 'Your message goes here')
        try:
            send_mess(448010439, msg) # nash
            if descr != "test":
                send_mess(96319578, msg) # brukida
        except:
            pass

        cart.clear()

        return cls(
            ok=True,
            order=order,
            #cart=Item.objects.filter(cart_id=cart.cart.id),
            #cart_summary=CartSummaryType(sum=cart.summary(), cnt=cart.count())
        )



class Mutation():
    order = OrderX.Field()
