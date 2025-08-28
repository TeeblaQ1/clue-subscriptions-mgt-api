from flask import Blueprint, request
from marshmallow import ValidationError
from app.decorators.security import jwt_required, admin_required
from app.utils.response import make_response
from app.models.subscriptions import Subscription, SubscriptionPlan
from app import db
from app.schema.subscriptions import SubscriptionSchema, SubscriptionPlanSchema
from datetime import datetime, timedelta
from sqlalchemy import text

subscription_schema = SubscriptionSchema()
plan_schema = SubscriptionPlanSchema()

bp = Blueprint("subscriptions", __name__, url_prefix="/api/subscriptions")


@bp.route("/plans", methods=["POST"])
@admin_required
def create_plan(user_id):
    """
    Create a new subscription plan.
    
    OPTIMIZATION: Uses ORM for simple CRUD operations where overhead is minimal.
    This endpoint performs simple operations that don't benefit from raw SQL.
    """
    data = request.get_json()
    try:
        data = plan_schema.load(data)
    except ValidationError as e:
        return make_response(message="Invalid input", error=e.messages, status_code=400)
    
    name = data["name"]
    description = data["description"]
    price_cents = data["price_cents"]
    
    # OPTIMIZATION: Simple uniqueness check using ORM - efficient for single record lookups
    if db.session.query(SubscriptionPlan).filter_by(name=name).first():
        return make_response(message="Plan already exists", status_code=400)
    
    plan = SubscriptionPlan(name=name, description=description, price_cents=price_cents)
    db.session.add(plan)
    db.session.commit()
    return make_response(message="Plan created successfully", data=plan.to_dict(), status_code=201)

@bp.route("/plans", methods=["GET"])
def list_plans():
    """
    List all subscription plans.
    
    OPTIMIZATION: Uses ORM for simple SELECT operations.
    Plans table is typically small, so ORM overhead is negligible.
    """
    plans = db.session.query(SubscriptionPlan).all()
    return make_response(message="Plans fetched successfully", data=[plan.to_dict() for plan in plans], status_code=200)

@bp.route("/subscribe", methods=["POST"])
@jwt_required
def subscribe(user_id):
    """
    Subscribe to a subscription plan.
    
    OPTIMIZATION: Uses raw SQL for subscription cancellation to avoid multiple database round trips.
    This eliminates the need for separate SELECT + UPDATE operations.
    """
    data = request.get_json()
    try:
        data = subscription_schema.load(data)
    except ValidationError as e:
        return make_response(message="Invalid input", error=e.messages, status_code=400)
    
    plan_id = data["plan_id"]
    duration_days = data["duration_days"]
    
    # OPTIMIZATION: Simple plan lookup using ORM - efficient for single record by primary key
    plan = db.session.query(SubscriptionPlan).filter_by(id=plan_id).first()
    if not plan:
        return make_response(message="Plan not found", status_code=404)
    
    # OPTIMIZATION: Raw SQL for subscription cancellation
    # This avoids the overhead of using the ORM for complex UPDATE operations
    now = datetime.now()
    active_query = text("""
        UPDATE subscriptions
        SET status = 'cancelled', ends_at = :now
        WHERE user_id = :uid AND status = 'active'
    """)
    db.session.execute(active_query, {"now": now, "uid": user_id})
    
    # Create new subscription using ORM for simple INSERT operations
    subscription = Subscription(user_id=user_id, plan_id=plan_id, starts_at=now, ends_at=now + timedelta(days=duration_days))
    db.session.add(subscription)
    db.session.commit()
    return make_response(message="Subscription created successfully", data=subscription.to_dict(), status_code=200)

@bp.route("/change-plan", methods=["POST"])
@jwt_required
def change_plan(user_id):
    """
    Change the plan of an active subscription.
    
    OPTIMIZATION: Uses single JOIN query to fetch subscription and plan in one database round trip.
    This eliminates the need for two separate queries and improves performance.
    """
    data = request.get_json()
    
    plan_id = data.get("plan_id")
    if not plan_id:
        return make_response(message="Plan ID is required", status_code=400)
    
    # OPTIMIZATION: Single JOIN query instead of two separate queries
    # This fetches both the subscription and plan details in one database round trip
    query = text("""
        SELECT s.id, s.user_id, s.plan_id, s.status, s.starts_at, s.ends_at,
               p.id as new_plan_id, p.name as new_plan_name, p.description as new_plan_description
        FROM subscriptions s
        CROSS JOIN plans p
        WHERE s.user_id = :uid AND s.status = 'active' AND p.id = :plan_id
        LIMIT 1
    """)
    
    result = db.session.execute(query, {"uid": user_id, "plan_id": plan_id}).mappings().first()
    
    if not result:
        # Check if user has no active subscription
        subscription_check = db.session.query(Subscription).filter_by(user_id=user_id, status="active").first()
        if not subscription_check:
            return make_response(message="You do not have an active subscription to change", status_code=400)
        else:
            return make_response(message="Plan not found", status_code=404)
    
    # Update the subscription with the new plan
    subscription = db.session.query(Subscription).filter_by(id=result.id).first()
    subscription.plan_id = plan_id
    db.session.commit()
    
    return make_response(message="Subscription plan changed successfully", data=subscription.to_dict(), status_code=200)


@bp.route("/cancel", methods=["POST"])
@jwt_required
def cancel_subscription(user_id):
    """
    Cancel the user's active subscription.
    
    OPTIMIZATION: Uses raw SQL to avoid SELECT + UPDATE overhead.
    This is a performance-critical operation that benefits from direct database execution.
    
    No request body required since the assumption is that the user will be cancelling 
    their own active subscription.

    OPTIMIZATION: Raw SQL for subscription cancellation
    This eliminates the overhead of using the ORM and avoids select + update in separate steps
    """
    query = text("""
        UPDATE subscriptions
        SET status = 'cancelled', ends_at = :now
        WHERE user_id = :uid AND status = 'active'
    """)
    db.session.execute(query, {"now": datetime.now(), "uid": user_id})
    db.session.commit()
    return make_response(message="Subscription cancelled successfully", status_code=200)

@bp.route("/active", methods=["GET"])
@jwt_required
def get_active_subscription(user_id):
    """
    Get the user's current active subscription.
    
    OPTIMIZATION: Uses raw SQL with JOIN to avoid ORM overhead and leverage database indexes.
    This query is performance-critical and benefits from direct SQL execution.

    OPTIMIZATION: Raw SQL join using indexes on (user_id, status, ends_at) to speed up the query
    """
    query = text("""
             SELECT s.id, p.name, p.description, p.id as plan_id, s.starts_at, s.ends_at, s.status
             FROM subscriptions s
             JOIN plans p ON p.id = s.plan_id
             WHERE s.user_id = :uid AND s.status = 'active'
             AND (s.ends_at IS NULL OR s.ends_at > :now)
             ORDER BY s.starts_at DESC
             LIMIT 1
             """)
    subscription = db.session.execute(query, {"uid": user_id, "now": datetime.now()}).mappings().first()
    return make_response(message="Active subscription fetched successfully", data=dict(subscription) if subscription else None, status_code=200)

@bp.route("/active/all", methods=["GET"])
@admin_required
def get_all_active_subscriptions(user_id):
    """
    Get all active subscriptions (admin only).
    
    OPTIMIZATION: Uses raw SQL to avoid ORM overhead for bulk operations.
    This endpoint can return many records, making ORM overhead significant.
    """
    user_ids = request.args.get("user_ids", None)
    if user_ids:
        user_ids = user_ids.split(",")
    else:
        user_ids = None
    
    # OPTIMIZATION: Using raw SQL avoids ORM overhead like object instantiation for every row
    # This is crucial for bulk operations where many records are returned
    query_str = """
        SELECT s.user_id, s.id, p.name, p.description, p.id as plan_id, s.starts_at, s.ends_at, s.status
        FROM subscriptions s
        JOIN plans p ON p.id = s.plan_id
        WHERE s.status = 'active'
        AND (s.ends_at IS NULL OR s.ends_at > :now)
    """

    params = {"now": datetime.now()}

    # OPTIMIZATION: Dynamic query construction with parameterized placeholders
    # This prevents SQL injection while maintaining query efficiency
    # if user_ids is provided, add the user_ids to the query using placeholders
    if user_ids:
        placeholders = ", ".join(f":uid{i}" for i in range(len(user_ids)))
        query_str += f" AND s.user_id IN ({placeholders})"
        for i, uid in enumerate(user_ids):
            params[f"uid{i}"] = uid

    query = text(query_str)
    subscriptions = db.session.execute(query, params).mappings().fetchall()
    return make_response(message="All active subscriptions fetched successfully", data=[dict(subscription) for subscription in subscriptions], status_code=200)

@bp.route("/history", methods=["GET"])
@jwt_required
def get_subscription_history(user_id):
    """
    Get paginated subscription history for the authenticated user.
    
    OPTIMIZATION: Uses raw SQL with pagination to prevent memory issues and improve performance.
    This endpoint can return large datasets, making pagination and raw SQL essential.
    """
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    offset = (page - 1) * page_size
    
    # OPTIMIZATION: For subscription history, pagination is introduced for optimization
    # Raw SQL with limit/offset is used here to avoid the overhead of using the ORM
    query = text("""
             SELECT s.id, p.name, p.description, p.id as plan_id, s.starts_at, s.ends_at, s.status
             FROM subscriptions s
             JOIN plans p ON p.id = s.plan_id
             WHERE s.user_id = :uid
             ORDER BY s.starts_at DESC
             LIMIT :limit OFFSET :offset
             """)
    subscriptions = db.session.execute(query, {"uid": user_id, "limit": page_size, "offset": offset}).mappings().fetchall()
    return make_response(message="Subscription history fetched successfully", data=[dict(subscription) for subscription in subscriptions], status_code=200)
