from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel, Field


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host="redis-12255.crce204.eu-west-2-3.ec2.redns.redis-cloud.com",
    port=12255,
    password="w3jNBqrXHoxS9OcxevoibfeaCQH6VTMT",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Inventory Service"}

@app.get("/products")
def all():
    return [ format(pk) for pk in Product.all_pks()]



@app.post("/products")
def create(product: Product):
    return product.save()

@app.get("/products/{pk}")
def get(pk: str):
    product = Product.get(pk)
    return format(product.pk)

def format(pk:str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }

@app.delete("/products/{pk}")
def delete(pk: str):
    product = Product.get(pk)
    product.delete(pk)
    return {"message": "Product deleted successfully"}