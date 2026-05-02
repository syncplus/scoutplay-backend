from contextvars import ContextVar

correlationId: ContextVar[str] = ContextVar('correlationId', default=None)
