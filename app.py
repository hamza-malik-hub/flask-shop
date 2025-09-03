from flask import Flask, render_template, session, redirect, url_for, request
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Product list with categories
global_products = [
    # Shirts
    {"id": 1, "name": "Classic T-Shirt", "price": 15.99, "image": "tshirtblack.jpeg", "category": "Shirts"},
    {"id": 15, "name": "White T-Shirt", "price": 18.99, "image": "shirt.jpeg", "category": "Shirts"},
    {"id": 16, "name": "Print T-shirt", "price": 22.67, "image": "product1.jpeg", "category": "Shirts"},
    {"id": 8, "name": "Polo Black Shirt", "price": 19.99, "image": "poloblack.jpeg", "category": "Shirts"},
    {"id": 9, "name": "Button-up", "price": 22.99, "image": "buttonup1.jpeg", "category": "Shirts"},
    {"id": 10, "name": "Button-up Black", "price": 22.99, "image": "buttonup2.jpeg", "category": "Shirts"},

    # Jackets
    {"id": 19, "name": "Leather Jacket", "price": 98.77, "image": "product4.jpeg", "category": "Jackets"},

    # Jeans
    {"id": 2, "name": "Blue Jeans", "price": 39.99, "image": "bluejeans.jpeg", "category": "Jeans"},
    {"id": 3, "name": "Stylish Jeans", "price": 42.99, "image": "jeans.jpeg", "category": "Jeans"},
    {"id": 17, "name": "Black Jeans", "price": 33.90, "image": "product2.jpeg", "category": "Jeans"},

    # Pants
    {"id": 6, "name": "Cargo Black Pants", "price": 34.99, "image": "cargoblack.jpeg", "category": "Pants"},
    {"id": 7, "name": "Cargo Brown Pants", "price": 34.99, "image": "cargobrown.jpeg", "category": "Pants"},

    # Shoes
    {"id": 18, "name": "Sports Shoes Black", "price": 65.70, "image": "product3.jpeg", "category": "Shoes"},
    {"id": 4, "name": "Sports Shoes White", "price": 59.99, "image": "shoes.jpeg", "category": "Shoes"},
    {"id": 5, "name": "Airforce Shoes", "price": 64.99, "image": "airforceshoes.jpeg", "category": "Shoes"},
    {"id": 11, "name": "Brown Chelsea Boots", "price": 74.99, "image": "brownchelsea.jpeg", "category": "Shoes"},
    {"id": 12, "name": "Black Chelsea Boots", "price": 74.99, "image": "blackchelsea.jpeg", "category": "Shoes"},
    {"id": 13, "name": "Leather Shoes", "price": 84.99, "image": "leathershoes.jpeg", "category": "Shoes"},
    {"id": 14, "name": "Leather Shoes Brown", "price": 84.99, "image": "leathershoesbrown.jpeg", "category": "Shoes"},
]


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/shop")
def shop():
    category = request.args.get("category")  # get selected category from URL

    # If a category is chosen, filter products
    if category:
        filtered_products = [p for p in global_products if p["category"] == category]
    else:
        filtered_products = global_products  # show all if no filter

    # Get all categories for dropdown
    categories = sorted(set([p["category"] for p in global_products]))

    return render_template(
        "shop.html",
        products=filtered_products,
        categories=categories,
        selected_category=category
    )


@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', [])

    # Quantity from form
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1

    # Get product info
    product = next((p for p in global_products if p["id"] == product_id), None)

    if product:
        found = False
        for item in cart:
            if isinstance(item, dict) and item["id"] == product_id:
                item["quantity"] += quantity
                found = True
                break
        if not found:
            cart.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })

    session['cart'] = cart
    session.modified = True

    return redirect(url_for('shop'))

@app.route('/cart')
def view_cart():
    raw_cart = session.get('cart', [])
    cart = [item for item in raw_cart if isinstance(item, dict)]
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route('/payment')
def payment():
    raw_cart = session.get('cart', [])
    cart = [item for item in raw_cart if isinstance(item, dict)]
    if not cart:
        return redirect(url_for('shop'))
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("payment.html", cart=cart, total=total)

@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('shop'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



if __name__ == "__main__":
    app.run(debug=True)
