import sentry_sdk

from core.config import settings


def init_sentry():

    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,

        traces_sample_rate=1.0,

        send_default_pii=True
    )