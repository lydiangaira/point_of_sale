import os
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from decimal import Decimal
from uuid import UUID

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "test-refresh-secret"

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
os.environ["JWT_PRIVATE_KEY"] = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
os.environ["JWT_PUBLIC_KEY"] = _private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.models.sale import Sale, SaleStatus

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app.state.limiter.enabled = False


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _create_user(db, *, username, role, password="TestPass123"):
    user = User(
        username=username,
        first_name="Test",
        last_name="User",
        email=f"{username}@example.com",
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, password


def _login(client, username, password):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client):
    db = TestingSessionLocal()
    try:
        user, password = _create_user(db, username="admin_user", role=UserRole.ADMIN)
    finally:
        db.close()
    return _login(client, user.username, password)


@pytest.fixture
def manager_auth_headers(client):
    db = TestingSessionLocal()
    try:
        user, password = _create_user(db, username="manager_user", role=UserRole.STORE_MANAGER)
    finally:
        db.close()
    return _login(client, user.username, password)


@pytest.fixture
def member_auth_headers(client):
    db = TestingSessionLocal()
    try:
        user, password = _create_user(db, username="sales_user", role=UserRole.SALES_ASSOCIATE)
    finally:
        db.close()
    return _login(client, user.username, password)

@pytest.fixture
def pending_sale_factory():
    def _factory(user_id, customer_id=None):
        db = TestingSessionLocal()
        try:
            sale = Sale(
                user_id=UUID(str(user_id)),
                customer_id=UUID(str(customer_id)) if customer_id else None,
                status=SaleStatus.PENDING,
                subtotal=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                total_amount=Decimal("0.00"),
            )
            db.add(sale)
            db.commit()
            db.refresh(sale)
            return sale
        finally:
            db.close()
    return _factory