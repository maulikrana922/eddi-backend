import json
import stripe
import datetime
from .models import *
from django.http import HttpResponse
from rest_framework.views import csrf_exempt
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeWebhookActions:

    def intent_succeeded(self, event):
        intent = event.data.object
        print(intent)

    def balance_updated(self, event):
        balance_obj = event.data.object
        print(balance_obj)

    def account_updated(self, event):
        obj = event.data.object
        print(obj)


    # def charge_succeeded(self, event):
    #     charge = event.data.object
    #     ach_charge = payment_models.ACHCharge.objects.filter(
    #         charge__id=charge['id']).first()
    #     if ach_charge:
    #         if ach_charge.charge['status'] != 'succeeded':
    #             ach_charge.charge = charge
    #             ach_charge.save()

    # def customer_subscription_updated(self, event):
    #     subscription = event.data.object
    #     payment_models.Price.objects.filter(
    #         subscription__id=subscription['id']).update(subscription=subscription)

    # def delete_subscription(self, event):
    #     subscription = event.data.object
    #     payment_models.Price.objects.filter(subscription__id=subscription['id']).update(
    #         subscription=subscription, subscription_active=False)

    # def invoice_payment_failed(self, event):
    #     invoice = event.data.object
    #     user = payment_models.Customer.objects.get(
    #         id=invoice['customer']).user
    #     amount = invoice['amount_due'] / 100
    #     Notification.objects.create(
    #         user=user,
    #         title='Subscription invoice payout failed!',
    #         content=f'Your payment for ${amount} has failed',
    #         additional={'subscription_id': invoice['subscription']}
    #     )

    # def invoice_payment_action_required(self, event):
    #     invoice = event.data.object
    #     user = payment_models.Customer.objects.get(
    #         id=invoice['customer']).user
    #     amount = invoice['amount_due'] / 100
    #     Notification.objects.create(
    #         user=user,
    #         title='Payment action required',
    #         content=f'Your payment for ${amount} requires action',
    #         additional={'subscription_id': invoice['subscription']}
    #     )

    # def invoice_upcoming_notification(self, event):
    #     invoice = event.data.object
    #     user = payment_models.Customer.objects.get(
    #         id=invoice['customer']).user
    #     amount = invoice['amount_due'] / 100
    #     Notification.objects.create(
    #         user=user,
    #         title='Upcoming Invoice',
    #         content=f"Payment will occur for subscription (ID: {invoice['subscription']}) for ${amount}",
    #         additional={'subscription_id': invoice['subscription']}
    #     )

    # def invoice_paid(self, event):
    #     invoice = event.data.object
    #     price_obj = payment_models.Price.objects.filter(
    #         subscription__id=invoice['subscription']).first()
    #     if price_obj and invoice['billing_reason'] != 'subscription_create':
    #         mission_models.MissionContribution.objects.create(
    #             is_anonymous=price_obj.user.is_anonymous_user,
    #             amount=price_obj.unit_amount,
    #             type_of_method='subscription',
    #             user=price_obj.user,
    #             mission=price_obj.mission,
    #         )

    WEBHOOK_HANDLER_MAP = {
        'payment_intent.succeeded': intent_succeeded,
        'balance.available': balance_updated,
        'account.updated': account_updated,
        # 'charge.succeeded': charge_succeeded,
        # 'customer.subscription.updated': customer_subscription_updated,
        # 'customer.subscription.deleted': delete_subscription,
        # 'invoice.payment_failed': invoice_payment_failed,
        # 'invoice.payment_action_required': invoice_payment_action_required,
        # 'invoice.upcoming': invoice_upcoming_notification,
        # 'invoice.paid': invoice_paid,
    }


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None
    actions = StripeWebhookActions()

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key)
    except ValueError as e:
        return HttpResponse(status=400)

    webhook_handler = actions.WEBHOOK_HANDLER_MAP.get(event.type)
    if webhook_handler:
        webhook_handler(StripeWebhookActions, event)
        return HttpResponse(status=200)

    return HttpResponse(status=404)
