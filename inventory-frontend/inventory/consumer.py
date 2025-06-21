from main import redis, Product
import time



key = "order_completed"
group = "inventory-group" # redis consumer group name

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
            # Process each message in the stream
            # results is a list of lists, where each inner list contains:
            # [stream_name (str), list of messages].
            # Each message is a tuple of (message_id (str), message_data (dict) with order details).

            for result in results:
                obj = result[1][0][1]
                
                try:
                    # Update the product quantity based on the order    
                    product = Product.get(obj["product_id"])
                    product.quantity -= int(obj["quantity"]) 
                    product.save()
                    print(f"Updated product {obj['product_id']} quantity to {product.quantity}")
                except Exception as e:
                    print(f"Error updating product {obj['product_id']}: {str(e)}")
                    redis.xadd("refund_order", obj, "*")


    except Exception as e:
        print(str(e))
        time.sleep(1)