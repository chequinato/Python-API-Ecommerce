from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommercedb.db'
db = SQLAlchemy(app)


#Modelagem
#Produto (id, nome, preco, descrição)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/api/products/add', methods=['POST'])
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
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"})

    return jsonify({"message": "Product not found"}), 404

# Definir uma rota raiz (página inicial) e a função que será executada ao requisitar

@app.route('/')
def hello_world ():
    return "Hello world!"

if __name__ == '__main__':
    app.run(debug=True)