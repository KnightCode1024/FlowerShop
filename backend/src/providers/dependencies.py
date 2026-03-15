from providers.api.yoomoney import YoomoneyProvider
from schemas.invoice import Methods


def yoomoney_factory():
    return YoomoneyProvider()


factories = {
    Methods.YOOMONEY: yoomoney_factory
}
