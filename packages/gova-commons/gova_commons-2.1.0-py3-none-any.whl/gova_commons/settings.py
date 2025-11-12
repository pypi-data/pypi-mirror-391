import logging
import sys


# Kafka
KAFKA_MODERATOR_EVENTS_TOPIC = "channel-1"

# Redis
REDIS_EMAIL_VERIFICATION_KEY_PREFIX = "email_verification:"
REDIS_STRIPE_INVOICE_METADATA_KEY_PREFIX = "stripe_invoice_metadata:"
REDIS_USER_MODERATOR_MESSAGES_PREFIX = "moderator_messages:"
REDIS_EXPIRY = 900

# Logging
logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
)
logger.addHandler(handler)
del logger

kafka_logger = logging.getLogger("kafka")
kafka_logger.setLevel(logging.CRITICAL)
del kafka_logger

stripe_logger = logging.getLogger("stripe")
stripe_logger.setLevel(logging.CRITICAL)
del stripe_logger
