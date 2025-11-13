from gova_commons.enums import PricingTierType


# Kafka
KAFKA_MODERATOR_EVENTS_TOPIC = "channel-1"

# Redis
REDIS_EMAIL_VERIFICATION_KEY_PREFIX = "email_verification:"
REDIS_STRIPE_INVOICE_METADATA_KEY_PREFIX = "stripe_invoice_metadata:"
REDIS_USER_MODERATOR_MESSAGES_PREFIX = "moderator_messages:"
REDIS_EXPIRY = 900

# PricingTier
PRICING_TIER_LIMITS = {
    PricingTierType.FREE: {
        "max_messages": 1000,
        "max_moderators": 1,
    },
    PricingTierType.PRO: {
        "max_messages": 10_000,
        "max_moderators": 5,
    },
    PricingTierType.ENTERPRISE: {
        "max_messages": 100_000,
        "max_moderators": 50,
    },
}
