from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.rate_limit import limiter
from app.routers import (
    auth as auth_router,
    category as category_router,
    customer as customer_router,
    payment as payment_router,
    product as product_router,
    receipt as receipt_router,
    sale as sale_router,
    supplier as supplier_router,
    user as user_router,
    sale_item as sale_item_router,
)

app = FastAPI(title="POS API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(category_router.router)
app.include_router(supplier_router.router)
app.include_router(product_router.router)
app.include_router(customer_router.router)
app.include_router(sale_router.router)
app.include_router(payment_router.router)
app.include_router(receipt_router.router)
app.include_router(sale_item_router.router)