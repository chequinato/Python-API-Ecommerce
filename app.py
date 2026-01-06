from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommercedb.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
CORS(app)

# =====================
# MODELS
# =====================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# =====================
# LOGIN
# =====================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.password == data.get('password'):
        login_user(user)
        return jsonify({"message": "Logged in successfully!"})

    return jsonify({"message": "Unauthorized"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

# =====================
# PRODUCTS
# =====================

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "nome": p.nome,
            "preco": p.preco
        } for p in products
    ])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    return jsonify({
        "id": product.id,
        "nome": product.nome,
        "preco": product.preco,
        "descricao": product.descricao
    })

@app.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.json

    product = Product(
        nome=data['nome'],
        preco=data['preco'],
        descricao=data.get('descricao')
    )

    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added successfully!"}), 201

@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    product.nome = data.get('nome', product.nome)
    product.preco = data.get('preco', product.preco)
    product.descricao = data.get('descricao', product.descricao)

    db.session.commit()
    return jsonify({"message": "Product updated successfully!"})

@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully!"})

# =====================
# CART
# =====================

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    cart_item = CartItem(
        user_id=current_user.id,
        product_id=product.id
    )

    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Product added to cart!"})

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    cart = []
    for item in items:
        product = db.session.get(Product, item.product_id)
        cart.append({
            "item_id": item.id,
            "product_id": product.id,
            "nome": product.nome,
            "preco": product.preco
        })

    return jsonify(cart)

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"})


@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(current_user.id)
    cart_items = user.cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Checkout completed, cart is now empty!"})

# =====================
# INIT
# =====================

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "API rodando 🚀"

if __name__ == '__main__':
    app.run(debug=True)
