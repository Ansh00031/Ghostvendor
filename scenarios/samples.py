"""Preloaded fragile target scenarios for GhostVendor resilience testing."""

SCENARIOS = {
    "Stripe Payment Processing": {
        "vendor": "Stripe",
        "description": "Payment handler that expects specific nested customer fields without error handling or null checks.",
        "code": '''import time

def process_checkout(payment_payload, stripe_client):
    """
    Process an incoming checkout session using Stripe API.
    Fragile: Assumes customer, charges, and email always exist in standard format.
    """
    # Create or retrieve customer charge
    charge = stripe_client.charges.create(
        amount=payment_payload["amount"],
        currency="usd",
        source=payment_payload["token"]
    )
    
    # Direct dictionary index access without .get() or try/except
    customer_id = charge["customer"]["id"]
    customer_email = charge["billing_details"]["email"]
    transaction_id = charge["id"]
    receipt_url = charge["receipt_url"]
    
    return {
        "status": "success",
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "email": customer_email,
        "receipt": receipt_url
    }
''',
        "entry_point": "process_checkout",
        "sample_input": {
            "amount": 2500,
            "token": "tok_visa_4242"
        },
        "baseline_mock_response": {
            "id": "ch_3N8x7b2eZvKYlo2C1g9abcde",
            "customer": {"id": "cus_N4v9pQ12ab"},
            "billing_details": {"email": "user@example.com"},
            "receipt_url": "https://stripe.com/receipts/ch_3N8x7b2e"
        },
        "supported_chaos": ["Schema Drift: Field Renamed", "HTTP 500 Outage", "Rate Limit (429)", "Missing Nested Keys"]
    },

    "SendGrid Notification Service": {
        "vendor": "SendGrid",
        "description": "Email dispatch service lacking timeout guards, retries, or circuit breaker protection.",
        "code": '''import time

def send_welcome_email(user_data, sendgrid_client):
    """
    Dispatches onboarding email to newly registered user.
    Fragile: Fails immediately if SendGrid rate limits (429) or times out.
    """
    payload = {
        "personalizations": [{
            "to": [{"email": user_data["email"], "name": user_data["name"]}],
            "subject": "Welcome to the Platform!"
        }],
        "from": {"email": "no-reply@company.com", "name": "Security Team"},
        "content": [{
            "type": "text/plain",
            "value": f"Hi {user_data['name']}, welcome aboard!"
        }]
    }
    
    # Single attempt call with no retry or backoff
    response = sendgrid_client.mail.send.post(request_body=payload)
    
    # Direct status code check assuming 202 is always returned
    if response.status_code != 202:
        raise RuntimeError(f"Email dispatch failed: {response.body}")
        
    return {
        "delivered": True,
        "message_id": response.headers["X-Message-Id"]
    }
''',
        "entry_point": "send_welcome_email",
        "sample_input": {
            "email": "alex@startup.io",
            "name": "Alex Chen"
        },
        "baseline_mock_response": {
            "status_code": 202,
            "body": "Accepted",
            "headers": {"X-Message-Id": "msg_sg_98741029481"}
        },
        "supported_chaos": ["Rate Limit (429)", "HTTP 503 Overloaded", "Network Timeout (10s)", "Malformed Response Header"]
    },

    "Auth0 User Profile Sync": {
        "vendor": "Auth0",
        "description": "OAuth token and profile sync that crashes if unannounced claims or metadata changes occur.",
        "code": '''import time

def sync_auth0_user(token_string, auth0_client):
    """
    Sync user profile data from Auth0 management API.
    Fragile: Assumes identities array and app_metadata structure never drift.
    """
    user_info = auth0_client.users.get(token_string)
    
    # Fragile assumption of array index 0 and nested provider keys
    primary_identity = user_info["identities"][0]
    provider = primary_identity["provider"]
    connection = primary_identity["connection"]
    tier = user_info["app_metadata"]["subscription_tier"]
    
    return {
        "user_id": user_info["user_id"],
        "email": user_info["email"],
        "provider": provider,
        "connection": connection,
        "tier": tier
    }
''',
        "entry_point": "sync_auth0_user",
        "sample_input": "auth0|64810294819abc",
        "baseline_mock_response": {
            "user_id": "auth0|64810294819abc",
            "email": "dev@company.com",
            "identities": [
                {"provider": "google-oauth2", "connection": "google"}
            ],
            "app_metadata": {
                "subscription_tier": "enterprise"
            }
        },
        "supported_chaos": ["Schema Drift: Missing Key", "Empty Array Crash", "HTTP 401 Token Expired", "Data Type Mutation"]
    },

    "OpenAI LLM Assistant": {
        "vendor": "OpenAI",
        "description": "AI prompt completion routine without token length guards or transient error handling.",
        "code": '''import time

def generate_summary(prompt_text, openai_client):
    """
    Calls OpenAI ChatCompletion API for document summary.
    Fragile: Direct indexing of choices[0].message.content without error checking.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_text}]
    )
    
    # Fragile chain of property accesses
    content = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    
    return {
        "summary": content.strip(),
        "tokens": tokens_used
    }
''',
        "entry_point": "generate_summary",
        "sample_input": "Summarize this quarterly financial report in 3 sentences.",
        "baseline_mock_response": {
            "choices": [{
                "message": {"content": "Revenue grew 14% year-over-year. Margins expanded. Guidance remains strong."}
            }],
            "usage": {"total_tokens": 142}
        },
        "supported_chaos": ["HTTP 500 Outage", "HTTP 429 Quota Exhausted", "Empty Choices Array", "Timeout"]
    }
}
