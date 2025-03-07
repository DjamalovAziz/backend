# backend\core\logging_middleware.py:

import logging
import time

logger = logging.getLogger("django")


class RequestLoggingMiddleware:
    """
    Middleware для логгирования информации о каждом HTTP запросе
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = int((time.time() - start_time) * 1000)

        status_code = getattr(response, "status_code", "-")
        method = getattr(request, "method", "-")

        logger.info(
            f"{method} {status_code}",
            extra={
                "request": request,
                "response": response,
                "duration_ms": duration,
            },
        )

        return response
