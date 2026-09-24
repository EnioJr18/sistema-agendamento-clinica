import logging
import time
import uuid

from django.conf import settings

logger = logging.getLogger('api.request')


class RequestLoggingMiddleware:
    """Loga metadados operacionais sem registrar headers ou payloads."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', '')
        if not request_id or len(request_id) > 64 or not request_id.replace('-', '').isalnum():
            request_id = uuid.uuid4().hex
        request.request_id = request_id
        inicio = time.monotonic()
        response = self.get_response(request)
        duracao_ms = round((time.monotonic() - inicio) * 1000, 2)
        response['X-Request-ID'] = request_id
        if settings.REQUEST_LOGGING_ENABLED:
            logger.info(
                'request_completed method=%s path=%s status=%s duration_ms=%s request_id=%s',
                request.method,
                request.path,
                response.status_code,
                duracao_ms,
                request_id,
            )
        return response
