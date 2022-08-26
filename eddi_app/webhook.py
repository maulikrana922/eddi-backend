import json
import stripe
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

    def payout_succeeded(self, event):
        obj = event.data.object
        print(obj.id)
        payout_obj = SupplierPayoutDetail.objects.get(**{"payout_id":obj.id})
        if payout_obj.supplier_account.total_amount_withdraw:
            payout_obj.supplier_account.total_amount_withdraw += float(payout_obj.amount/100)
        else:
            payout_obj.supplier_account.total_amount_withdraw = float(payout_obj.amount/100)
        payout_obj.supplier_account.save()
        payout_obj.save()
        html_path = SUPPLIER_PAYOUT_SUCCESSED_HTML
        fullname = payout_obj.supplier_account.supplier.first_name + " " + payout_obj.supplier_account.supplier.last_name
        context_data = {"amount": float(payout_obj.amount/100),"fullname":fullname}
        email_html_template = get_template(html_path).render(context_data)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (payout_obj.supplier_account.supplier.email_id,)
        email_msg = EmailMessage('Supplier Receives the Payment',email_html_template,email_from,recipient_list)
        email_msg.content_subtype = 'html'
        path = 'eddi_app'
        img_dir = 'static'  
        image = 'Logo.png'
        file_path = os.path.join(path,img_dir,image)
        with open(file_path,'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<{name}>'.format(name=image))
            img.add_header('Content-Disposition', 'inline', filename=image)
        email_msg.attach(img)
        email_msg.send(fail_silently=False)
        print(payout_obj)


    WEBHOOK_HANDLER_MAP = {
        'payment_intent.succeeded': intent_succeeded,
        'balance.available': balance_updated,
        'account.updated': account_updated,
        'payout.paid': payout_succeeded
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
