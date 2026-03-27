from providers.api.yoomoney import YoomoneyProvider
from providers.api.stripe_provider import StripeProvider
from schemas.invoice import Methods


def yoomoney_factory():
    return YoomoneyProvider()


def stripe_factory():
    return StripeProvider()


factories = {
    Methods.YOOMONEY: yoomoney_factory,
    Methods.STRIPE: stripe_factory,
}
