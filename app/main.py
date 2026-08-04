from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base


from routers.user import router as user_router
from routers.customer import router as customer_router
from routers.supplier import router as supplier_router
from routers.category import router as category_router
from routers.product import router as product_router
from routers.sale import router as sale_router
from routers.sale_item import router as sale_item_router
from routers.payment import router as payment_router
from routers.receipt import router as receipt_router

app = FastAPI(title="Secure POS Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home_redirect():
    """
    Landing checkpoint route providing clear landing information to system consumers.
    """
    return {"message": "Welcome to Shop Reverie POS Backend API."}


app.include_router(user_router)
app.include_router(customer_router)
app.include_router(supplier_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(sale_item_router)
app.include_router(payment_router)
app.include_router(receipt_router)
