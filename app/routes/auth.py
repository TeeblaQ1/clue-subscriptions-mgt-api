from flask import Blueprint, request
from marshmallow import ValidationError
from app.models import User
from app import db
from app.utils.auth_utils import AuthUtils
from app.utils.response import make_response
from app.schema.users import UserSchema

bp = Blueprint("auth", __name__, url_prefix="/api")

user_schema = UserSchema()

@bp.route("/register", methods=["POST"])
def register():
    """
    User registration endpoint.
    
    OPTIMIZATION: Uses ORM for simple operations but has optimization opportunities.
    This endpoint performs email uniqueness check that could benefit from database indexing.
    """
    data = request.get_json()

    try:
        data = user_schema.load(data)
    except ValidationError as e:
        return make_response(message="Invalid input", error=e.messages, status_code=400)
    
    email = data["email"]
    password = data["password"]

    # OPTIMIZATION OPPORTUNITY: Email uniqueness check
    if db.session.query(User).filter_by(email=email).first():
        return make_response(message="User already exists", status_code=400)
    
    # OPTIMIZATION: Simple user creation using ORM
    # This operation is efficient as it's a single INSERT operation
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # OPTIMIZATION: JWT token generation without additional database queries
    # This is stateless and efficient for authentication
    token = AuthUtils.generate_token(user.id)
    return make_response(message="User created successfully", data={"token": token, "user_id": user.id}, status_code=201)

@bp.route("/login", methods=["POST"])
def login():
    """
    User login endpoint.
    
    OPTIMIZATION: Uses ORM for authentication but has security and performance considerations.
    This endpoint performs password verification that could benefit from additional optimizations.
    """
    data = request.get_json()
    try:
        data = user_schema.load(data)
    except ValidationError as e:
        return make_response(message="Invalid input", error=e.messages, status_code=400)
    
    email = data["email"]
    password = data["password"]
    
    # OPTIMIZATION: User lookup by email
    # This query benefits from the unique index on email column
    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return make_response(message="Invalid credentials", status_code=401)
    
    # OPTIMIZATION: JWT token generation
    # This is stateless and efficient - no database writes required
    # The token contains all necessary user information
    token = AuthUtils.generate_token(user.id)
    return make_response(message="Login successful", data={"token": token, "user_id": user.id}, status_code=200)

