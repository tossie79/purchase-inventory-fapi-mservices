from main import redis, Order
import time



key = "refund_order"
group = "payment-group" # redis consumer group name

try:
    redis.xgroup_create(key, group)

except Exception as e:
    print(f"Group {group} already exists or error: {e}")



while True:
    try:
        # Read messages from the stream
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        
        if results != []:
            print(results)
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj["pk"])
                if order:
                    print(order)
                    order.status = "refunded"
                    order.save()
                else:
                    print(f"Order {obj['pk']} not found for refund.")


    except Exception as e:
        print(str(e))
        time.sleep(1)