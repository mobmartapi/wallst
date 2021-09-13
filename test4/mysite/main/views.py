from django.http import HttpResponse
from django.shortcuts import render, redirect
import stripe
import json
import djstripe
from django.http import JsonResponse
from djstripe.models import Product
from django.contrib.auth.decorators import login_required

# Create your views here.

def checkout(request):
    products = Product.objects.all()
    print(products)
    return render(request, "main/checkout.html", {"products": products})


def create_sub(request):
    print(request.method)
    if request.method == 'POST':
        # Reads application/json and returns a response
        data = json.loads(request.body)
        print(data)
        payment_method = data['payment_method']
        stripe.api_key = djstripe.settings.STRIPE_SECRET_KEY

        payment_method_obj = stripe.PaymentMethod.retrieve(payment_method)
        print(payment_method_obj)
        djstripe.models.PaymentMethod.sync_from_stripe_data(payment_method_obj)

        print(request.user)
        try:
            # This creates a new Customer and attaches the PaymentMethod in one API call.
            customer = stripe.Customer.create(
                payment_method=payment_method,
                # email=request.user.email,
                email="test@example.com",
                invoice_settings={
                    'default_payment_method': payment_method
                }
            )

            djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(
                customer)
            print(djstripe_customer)
            # request.user.customer = djstripe_customer

            # At this point, associate the ID of the Customer object with your
            # own internal representation of a customer, if you have one.
            # print(customer)

            # Subscribe the user to the subscription created
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price": data["price_id"],
                    },
                ],
                expand=["latest_invoice.payment_intent"]
            )

            djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(
                subscription)
            print(djstripe_subscription)
            # request.user.subscription = djstripe_subscription
            # request.user.save()

            return JsonResponse(subscription)
        except Exception as e:
            print(e)
            return JsonResponse({'error': (e.args[0])}, status=403)
    else:
        return HttpResponse('request method not allowed')


def complete(request):
    return render(request, "main/complete.html")
