import logging
from app.config import settings

class SecretMasker(logging.Filter):
    def __init__(self):
        super().__init__()
        self.secrets = [
            settings.gemini_api_key,
            settings.apify_api_key,
            settings.serpapi_api_key,
            settings.pinterest_password,
            settings.reddit_client_secret,
            settings.reddit_password
        ]
        self.secrets = [s for s in self.secrets if s]

    def filter(self, record):
        if not hasattr(record, "msg") or not isinstance(record.msg, str):
            return True
        for secret in self.secrets:
            if secret in record.msg:
                record.msg = record.msg.replace(secret, "***MASKED_SECRET***")
        return True

def configure_logger():
    logger = logging.getLogger()
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    # Add masker to all handlers
    masker = SecretMasker()
    for handler in logger.handlers:
        handler.addFilter(masker)

configure_logger()
class Logger:
    pass
