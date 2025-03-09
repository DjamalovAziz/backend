# backend\core\logging_middleware.py:

import logging
import time

# Используем логгер django, так как вы его используете в выводе
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

        # Важное изменение: явно передаем duration_ms как отдельное поле
        # вместо добавления в message
        logger.info(
            f"{method} {status_code}",
            extra={
                "request": request,
                "response": response,
                "duration_ms": duration,  # Это значение должно быть целым числом
            },
        )

        return response
