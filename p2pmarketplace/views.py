# p2pmarketplace/views.py
import os
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings

# Mock databases
USERS = {
    1: {"name": "Alice", "balance": 1000},
    2: {"name": "Bob", "balance": 1000},
    3: {"name": "Charlie", "balance": 1000},
}

PRODUCTS = [
    {"id": 1, "name": "Vintage Lamp", "price": 45, "seller_id": 1, "image": None},
    {"id": 2, "name": "Second-hand Bike", "price": 120, "seller_id": 2, "image": None},
    {"id": 3, "name": "Used Laptop", "price": 380, "seller_id": 3, "image": None},
]

TRANSACTIONS = []

@csrf_exempt
def api(request):
    """
    API endpoint for our P2P marketplace.
    Supports GET for fetching users, products, transactions, and searching.
    Supports POST for adding products and buying products.
    """
    if request.method == 'GET':
        action = request.GET.get("action")
        
        if action == "users":
            return JsonResponse({"users": USERS})
        elif action == "products":
            return JsonResponse({"products": PRODUCTS})
        elif action == "transactions":
            return JsonResponse({"transactions": TRANSACTIONS})
        elif action == "search":
            query = request.GET.get("q", "").lower()
            results = [p for p in PRODUCTS if query in p["name"].lower()]
            return JsonResponse({"results": results})
        return HttpResponseBadRequest("Unknown action")

    elif request.method == 'POST':
        data = request.POST.dict()
        action = data.get("action")

        if action == "add_product":
            try:
                seller_id = int(data['seller_id'])
                name = data['name']
                price = float(data['price'])
            except (KeyError, ValueError):
                return HttpResponseBadRequest("Invalid data provided")

            image = request.FILES.get('image')
            image_url = None
            if image:
                image_name = default_storage.save(image.name, image)
                image_url = os.path.join(settings.MEDIA_URL, image_name)

            product_id = len(PRODUCTS) + 1
            PRODUCTS.append({
                "id": product_id,
                "name": name,
                "price": price,
                "seller_id": seller_id,
                "image": image_url
            })
            return JsonResponse({"message": "Product added"})

        elif action == "buy_product":
            try:
                buyer_id = int(data['buyer_id'])
                product_id = int(data['product_id'])
            except (KeyError, ValueError):
                return HttpResponseBadRequest("Invalid data provided")

            product = next((p for p in PRODUCTS if p['id'] == product_id), None)
            if not product:
                return HttpResponseBadRequest("Product not found")
            if product['seller_id'] == buyer_id:
                return HttpResponseBadRequest("Cannot buy your own product")

            buyer = USERS.get(buyer_id)
            seller = USERS.get(product['seller_id'])
            if buyer is None or seller is None:
                return HttpResponseBadRequest("Invalid user")

            if buyer['balance'] < product['price']:
                return HttpResponseBadRequest("Insufficient balance")

            # Process payment
            buyer['balance'] -= product['price']
            seller['balance'] += product['price']

            # Record the transaction
            TRANSACTIONS.append({
                "id": len(TRANSACTIONS) + 1,
                "product": product['name'],
                "amount": product['price'],
                "buyer": buyer['name'],
                "seller": seller['name'],
                "timestamp": datetime.now().isoformat()
            })
            return JsonResponse({"message": "Transaction successful"})

        return HttpResponseBadRequest("Unknown action")

    return HttpResponseBadRequest("Invalid method")
