from fastapi import FastAPI
from auth_routers import auth_routers
from order_routers import order_routers
from product_routers import product_routers

app = FastAPI()

app.include_router(auth_routers)
app.include_router(order_routers)
app.include_router(product_routers)

@app.get('/')
async def home():
    return {"message": "Hello World"}