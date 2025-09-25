from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

# ---------------- Models ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=10)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)

# ---------------- Routes ----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/shop")
def shop():
    category = request.args.get("category")
    if category:
        filtered_products = Product.query.filter_by(category=category).all()
    else:
        filtered_products = Product.query.all()
    categories = sorted(set([p.category for p in Product.query.all()]))
    return render_template("shop.html", products=filtered_products, categories=categories, selected_category=category)

# ---------------- Cart Routes ----------------
@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', [])
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1

    product = Product.query.get(product_id)
    if product:
        found = False
        for item in cart:
            if item["id"] == product_id:
                item["quantity"] += quantity
                found = True
                break
        if not found:
            cart.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": quantity,
                "stock": product.stock  # <- This is required
            })

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('shop'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item["id"] != product_id]
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', [])
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] = min(quantity, item["stock"])
            break
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('shop'))

# ---------------- Payment ----------------
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('shop'))

    total = sum(item["price"] * item["quantity"] for item in cart)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        for item in cart:
            new_order = Order(
                product_id=item["id"],
                quantity=item["quantity"],
                customer_name=name,
                customer_email=email,
                customer_address=address
            )
            db.session.add(new_order)

            product = Product.query.get(item["id"])
            if product:
                product.stock -= item["quantity"]

        db.session.commit()
        session.pop('cart', None)
        return redirect(url_for('shop'))

    return render_template("payment.html", cart=cart, total=total)

# ---------------- Other Pages ----------------
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ---------------- Admin Routes ----------------
@app.route('/admin')
def admin_dashboard():
    products = Product.query.all()
    orders = Order.query.all()
    return render_template('admin_dashboard.html', products=products, orders=orders)

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        stock = int(request.form['stock'])

        file = request.files['image']
        if file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)
            image = "uploads/" + file.filename
        else:
            image = "default.jpg"

        new_product = Product(name=name, price=price, category=category, stock=stock, image=image)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        if product.image and product.image != "default.jpg":
            image_path = os.path.join(app.root_path, 'static', product.image)
            if os.path.exists(image_path):
                os.remove(image_path)
    except Exception as e:
        print("Error deleting image:", e)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ---------------- Main ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
