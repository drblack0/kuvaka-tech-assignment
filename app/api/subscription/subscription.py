# In your main routes file (e.g., app.py)

import os

from flask import jsonify, request
import stripe
from app.db.models import db, User  # Import your User model
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def create_pro_subscription(current_user):
    """Initiates a Stripe Checkout session for a Pro subscription."""
    if current_user.subscription_tier == "pro":
        return jsonify(
            {"status": False, "message": "User is already on the Pro plan"}
        ), 400

    stripe_customer_id = current_user.stripe_customer_id

    try:
        # If the user is not yet a customer in Stripe, create one
        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=f"{current_user.mobile}@example.com",  # Use a placeholder email
                name=current_user.username,
                metadata={"user_id": current_user.userid},
            )
            stripe_customer_id = customer.id
            # Save the new customer ID to our database
            current_user.stripe_customer_id = stripe_customer_id
            db.session.commit()

        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": os.environ.get("STRIPE_PRICE_KEY"),
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
        )

        # Return the URL for the client to redirect to
        return jsonify({"status": True, "checkout_url": checkout_session.url}), 200

    except Exception as e:
        print(f"[ERROR] in create_pro_subscription: {e}")
        return jsonify({"status": False, "message": f"Stripe error: {str(e)}"}), 500


def get_subscription_status(current_user):
    """Checks the user's current subscription tier."""
    return jsonify(
        {"status": True, "subscription_tier": current_user.subscription_tier}
    ), 200


def stripe_webhook(request):
    """Handles webhook events from Stripe."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.environ.get(
        "STRIPE_WEBHOOK_SECRET"
    )  # You need to create this!

    if not endpoint_secret:
        return jsonify(
            {"status": False, "message": "Webhook secret not configured"}
        ), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return jsonify({"status": False, "message": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"status": False, "message": "Invalid signature"}), 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        stripe_customer_id = session.get("customer")

        # Find the user in our database with this customer ID
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        if user:
            # Update the user's subscription tier to 'pro'
            user.subscription_tier = "pro"
            db.session.commit()
            print(f"User {user.username} successfully subscribed to Pro plan.")
    else:
        print(f"Unhandled Stripe event type: {event['type']}")

    # Acknowledge the event was received
    return jsonify({"status": "success"}), 200
