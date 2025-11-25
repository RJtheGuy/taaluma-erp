import logging
from django.core.mail import mail_admins
from logging.handlers import RotatingFileHandler
import os


class CustomRotatingFileHandler(RotatingFileHandler):
    """Custom rotating file handler with better formatting"""
    
    def __init__(self, filename, maxBytes=10485760, backupCount=5):
        # 10MB default max size
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount)


class AdminEmailHandler(logging.Handler):
    """Send critical errors to admins via email"""
    
    def emit(self, record):
        try:
            subject = f'Error: {record.levelname} - {record.getMessage()[:50]}'
            message = self.format(record)
            mail_admins(subject, message, fail_silently=True)
        except Exception:
            self.handleError(record)
