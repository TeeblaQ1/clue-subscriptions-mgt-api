from app.extensions import db
from sqlalchemy.sql import func

class SubscriptionPlan(db.Model):
    __tablename__ = "plans"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price_cents = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Plan {self.name}>"
    
    @property
    def price(self):
        return self.price_cents / 100

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price_cents": self.price_cents,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    status = db.Column(db.Enum("active", "cancelled", "expired", name="subscription_status"), nullable=False, default="active")
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    user = db.relationship("User", backref="subscriptions")
    plan = db.relationship("SubscriptionPlan", backref="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan.to_dict(),
            "status": self.status,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @property
    def is_active(self):
        return self.status == "active"
    
    @property
    def is_cancelled(self):
        return self.status == "cancelled"
    
    @property
    def is_expired(self):
        return self.status == "expired"

# composite index created to speed up active subscription queries
db.Index("idx_subscriptions_user_status_ends_at", Subscription.user_id, Subscription.status, Subscription.ends_at)