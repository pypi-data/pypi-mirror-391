"""
Polar Product and Price IDs Configuration
All product IDs and price IDs from Polar API
"""

# Product IDs (main products)
POLAR_PRODUCT_IDS = {
    "developer": {
        "monthly": "68443920-6061-434f-880d-83d4efd50fde",
        "annual": "e59df0ee-7287-4132-8edd-3b5fdf4a30f3",
    },
    "pro": {
        "monthly": "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b",
        "annual": "eb0d9d5a-fceb-485d-aaae-36b50d8731f4",
    },
    "team": {
        "monthly": "41768ba5-f37d-417d-a10e-fb240b702cb6",
        "annual": "2da941e8-450a-4498-a4a4-b3539456219e",
    },
}

# Price IDs (needed for checkout API)
POLAR_PRICE_IDS = {
    "developer": {
        "monthly": "570adac8-1909-401e-b2d5-f511bc624be3",  # $39/mo
        "annual": "5f26f7a8-1eb4-44c9-9fda-fc550239ed31",   # $390/yr
    },
    "pro": {
        "monthly": "1b583a0e-abba-42be-b644-afd750aaec84",  # $49/mo
        "annual": "f61d1a29-06af-4f5f-855d-0e8aafa99b6a",   # $490/yr
    },
    "team": {
        "monthly": "e769548a-5d26-4d92-bcfa-8b6627cefd83",  # $99/mo
        "annual": "59e496cc-03ac-4244-ab0c-3d6bb3a2c907",   # $990/yr
    },
}

# Meter ID for usage-based billing
POLAR_METER_ID = "9531345e-1c6d-4322-9d1a-618219cb69e5"

# Reverse mapping: Product ID → Tier + Billing
PRODUCT_ID_TO_TIER = {
    # Monthly
    "68443920-6061-434f-880d-83d4efd50fde": {"tier": "developer", "billing": "monthly"},
    "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b": {"tier": "pro", "billing": "monthly"},
    "41768ba5-f37d-417d-a10e-fb240b702cb6": {"tier": "team", "billing": "monthly"},
    # Annual
    "e59df0ee-7287-4132-8edd-3b5fdf4a30f3": {"tier": "developer", "billing": "annual"},
    "eb0d9d5a-fceb-485d-aaae-36b50d8731f4": {"tier": "pro", "billing": "annual"},
    "2da941e8-450a-4498-a4a4-b3539456219e": {"tier": "team", "billing": "annual"},
}

# Reverse mapping: Price ID → Tier + Billing
PRICE_ID_TO_TIER = {
    # Monthly
    "570adac8-1909-401e-b2d5-f511bc624be3": {"tier": "developer", "billing": "monthly"},
    "1b583a0e-abba-42be-b644-afd750aaec84": {"tier": "pro", "billing": "monthly"},
    "e769548a-5d26-4d92-bcfa-8b6627cefd83": {"tier": "team", "billing": "monthly"},
    # Annual
    "5f26f7a8-1eb4-44c9-9fda-fc550239ed31": {"tier": "developer", "billing": "annual"},
    "f61d1a29-06af-4f5f-855d-0e8aafa99b6a": {"tier": "pro", "billing": "annual"},
    "59e496cc-03ac-4244-ab0c-3d6bb3a2c907": {"tier": "team", "billing": "annual"},
}


def get_product_id(tier: str, billing: str = "monthly") -> str:
    """Get product ID for a tier and billing period"""
    return POLAR_PRODUCT_IDS.get(tier, {}).get(billing)


def get_price_id(tier: str, billing: str = "monthly") -> str:
    """Get price ID for a tier and billing period"""
    return POLAR_PRICE_IDS.get(tier, {}).get(billing)


def get_tier_from_product_id(product_id: str) -> dict:
    """Get tier and billing info from product ID"""
    return PRODUCT_ID_TO_TIER.get(product_id, {"tier": "none", "billing": "monthly"})


def get_tier_from_price_id(price_id: str) -> dict:
    """Get tier and billing info from price ID"""
    return PRICE_ID_TO_TIER.get(price_id, {"tier": "none", "billing": "monthly"})
