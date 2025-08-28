import time
from sqlalchemy import text
from app import db
from app.models import User, SubscriptionPlan, Subscription
from datetime import datetime, timedelta

def test_bulk_vs_naive(app):
    with app.app_context():
        p = SubscriptionPlan.query.first()

        # create users + subs
        users = []
        for i in range(500):
            u = User(email=f"user{i}@example.com")
            u.set_password("x")
            db.session.add(u)
            users.append(u)
        db.session.commit()

        subs = [
            Subscription(
                user_id=u.id,
                plan_id=p.id,
                status="active",
                starts_at=datetime.now(),
                ends_at=datetime.now() + timedelta(days=30),
            )
            for u in users
        ]
        db.session.add_all(subs)
        db.session.commit()

        ids = [u.id for u in users]

        # naive: N queries
        start = time.time()
        results_naive = []
        for uid in ids:
            query = text("SELECT * FROM subscriptions WHERE user_id = :uid AND status = 'active'")
            row = db.session.execute(query, {"uid": uid}).fetchall()
            results_naive.append(row)
        naive_t = time.time() - start

        # bulk: 1 query
        start = time.time()
        query_str = """
            SELECT s.user_id, s.id, p.name, p.description, p.id as plan_id,
                   s.starts_at, s.ends_at, s.status
            FROM subscriptions s
            JOIN plans p ON p.id = s.plan_id
            WHERE s.status = 'active'
            AND (s.ends_at IS NULL OR s.ends_at > :now)
        """
        params = {"now": datetime.now()}
        placeholders = ", ".join(f":uid{i}" for i in range(len(ids)))
        query_str += f" AND s.user_id IN ({placeholders})"
        for i, uid in enumerate(ids):
            params[f"uid{i}"] = uid

        query = text(query_str)
        subscriptions = db.session.execute(query, params).mappings().fetchall()
        results_bulk = [dict(subscription) for subscription in subscriptions]
        bulk_t = time.time() - start

        assert len(results_bulk) == len(ids)
        assert bulk_t * 5 < naive_t
