from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommercedb.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

#Modelagem
#User (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

#Produto (id, nome, preco, descrição)
class Product(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

#Autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and data.get('password') == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully!"})
    return jsonify({"message": "Unauthorized"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

with app.app_context():
    db.create_all()

@app.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()

    if not data or 'nome' not in data or 'preco' not in data:
        return jsonify({"message": "Invalid product data"}), 400

    product = Product(
        nome=data['nome'],
        preco=data['preco'],
        descricao=data.get('descricao')
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product added successfully!"}), 201


@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"})

    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "nome": product.nome,
            "preco": product.preco,
            "descricao": product.descricao
        })
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    if 'nome' in data:
        product.nome = data['nome']

    if 'preco' in data:
        product.preco = data['preco']

    if 'descricao' in data:
        product.descricao = data['descricao']

    db.session.commit()

    return jsonify({"message": "Product updated successfully!"})

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "nome": product.nome,
            "preco": product.preco,        }
        products_list.append(product_data)
    return jsonify(products_list)

# Definir uma rota raiz (página inicial) e a função que será executada ao requisitar

@app.route('/')
def hello_world ():
    return "Hello world!"

if __name__ == '__main__':
    app.run(debug=True)