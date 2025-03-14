# backend\utils\logging_filters.py:


import logging


class RequestInfoFilter(logging.Filter):
    """
    Filter that adds request-related information to logs
    """

    def filter(self, record):
        record.method = "-"
        record.status_code = "-"
        record.path = "-"
        record.remote_addr = "-"
        record.ua = "-"
        record.user = "anonymous"

        if not hasattr(record, "duration_ms"):
            record.duration_ms = "-"

        request = getattr(record, "request", None)

        if request and hasattr(request, "path"):
            record.method = getattr(request, "method", "-")
            record.path = request.path

            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                record.remote_addr = x_forwarded_for.split(",")[0].strip()
            else:
                record.remote_addr = request.META.get("REMOTE_ADDR", "-")

            record.ua = request.META.get("HTTP_USER_AGENT", "-")

            if hasattr(request, "user") and request.user.is_authenticated:
                record.user = request.user.username

        response = getattr(record, "response", None)
        if response and hasattr(response, "status_code"):
            record.status_code = response.status_code

        return True
