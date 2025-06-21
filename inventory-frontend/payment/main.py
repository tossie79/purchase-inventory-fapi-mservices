from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel, Field
# from starlette.requests import Request
# import requests
import httpx, time



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# this should be a different database

redis = get_redis_connection(
    host="redis-12255.crce204.eu-west-2-3.ec2.redns.redis-cloud.com",
    port=12255,
    password="w3jNBqrXHoxS9OcxevoibfeaCQH6VTMT",
    decode_responses=True
)


class Order(HashModel):
    product_id:str
    price:float
    fee: float
    total: float
    quantity: int
    status: str  # "pending", "completed", "refunded"
    class Meta:
        database = redis   


@app.get("/orders/{pk}")
def get(pk: str):
    order =  Order.get(pk)
    redis.xadd("refund_order", order.dict(), "*")
    return order

@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    product_id = body["id"]
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/products/{product_id}")
    product= response.json()

    order = Order(
        product_id = product_id ,
        price = product["price"],
        fee = 0.2 * product["price"],
        total = 1.2 * product["price"],
        quantity = body["quantity"],
        status = "pending"
    )
    order.save()
    # Simulate a background task to process the order
    # This could be an email notification, payment processing, etc.
    background_tasks.add_task(order_completed, order)

    return order



def order_completed(order: Order):
    time.sleep(5)  # Simulate a delay for order processing
    order.status = "completed"
    order.save()
    # Send a message to the inventory service to update the product quantity
    # This could be done via a message queue, webhook, etc.
    redis.xadd("order_completed", order.dict(), "*") #  order.dict() returns a dict representation of the order
    print(f"Order {order.pk} completed and message sent to inventory service.")
  