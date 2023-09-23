from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Criar API
app = Flask(__name__)

# Criar instância de SQLAlchemy
app.config['SECRET_KEY'] = 'CHAVE999TESTE999'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autor.db'

db = SQLAlchemy(app)
db: SQLAlchemy

# Definir a estrutura da tabela Obra


class Obra(db.Model):
    __tablename__ = 'obra'
    id_obra = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    sigla = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))

# Definir a estrututra da tabela Autor


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    obras = db.relationship('Obra')


def inicializar_banco():
    with app.app_context():
        # Executar o comando para criar banco de dados
        db.drop_all()
        db.create_all()
        # Criar usuários admnistradores
        autor = Autor(
            nome='Gabriel', email='teste@gmail.com',
            senha='123456', admin=True)
        db.session.add(autor)
        db.session.commit()


if __name__ == "__main__":
    inicializar_banco()
