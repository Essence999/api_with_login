from flask import jsonify, request, make_response
from estrutura_de_dados import Autor, Obra, app, db
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Rota padrão - GET https://localhost:5000


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            print
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um token, validar acesso consultando o Banco de Dados.
        try:
            resultado = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            autor = Autor.query.filter_by(
                id_autor=resultado['id_autor']).first()
        except Exception:
            return jsonify({'mensagem': 'Token é inválido.'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            'Login inválido', 401,
            {'WWW-Authenticate': 'Basic real="Login obrigatório."'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response(
            'Login inválido', 401,
            {'WWW-Authenticate': 'Basic real="Login obrigatório."'})
    if auth.password == usuario.senha:
        token = jwt.encode({
            'id_autor': usuario.id_autor,
            'exp': datetime.utcnow() + timedelta(minutes=30)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response(
        'Login inválido', 401,
        {'WWW-Authenticate': 'Basic real="Login obrigatório."'})


@app.route('/')
@token_obrigatorio
def obter_obras(autor):
    obras = Obra.query.all()

    list_obras = []
    for obra in obras:
        obra_atual = {}
        obra_atual['titulo'] = obra.titulo
        obra_atual['id_autor'] = obra.id_autor
        obra_atual['sigla'] = obra.sigla
        list_obras.append(obra_atual)
    return jsonify({'obras': list_obras})

# Obter obra por id - GET https://localhost:5000/obra/1


@app.route('/obra/<int:id_obra>', methods=['GET'])
@token_obrigatorio
def obter_obra_por_indice(autor, id_obra):
    obra = Obra.query.filter_by(id_obra=id_obra).first()
    obra_atual = {}
    try:
        obra_atual['titulo'] = obra.titulo
    except Exception:
        pass
    obra_atual['id_autor'] = obra.id_autor
    obra_atual['sigla'] = obra.sigla

    return jsonify({'obras': obra_atual})

# Criar uma nova obra - POST https://localhost:5000/obra


@app.route('/obra', methods=['POST'])
@token_obrigatorio
def nova_obra(autor):
    nova_obra = request.get_json()
    obra = Obra(
        titulo=nova_obra['titulo'], sigla=nova_obra['sigla'],
        id_autor=nova_obra['id_autor'])

    db.session.add(obra)
    db.session.commit()

    return jsonify({'mensagem': 'Obra criada com sucesso'})

# Alterar uma obra existente - PUT https://localhost:5000/obra/1


@app.route('/obra/<int:id_obra>', methods=['PUT'])
@token_obrigatorio
def alterar_obra(autor, id_obra):
    obra_alterada = request.get_json()
    obra = Obra.query.filter_by(id_obra=id_obra).first()
    try:
        obra.titulo = obra_alterada['titulo']
    except Exception:
        pass
    try:
        obra.id_autor = obra_alterada['id_autor']
    except Exception:
        pass
    try:
        obra.sigla = obra_alterada['siglea']
    except Exception:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Obra alterada com sucessso'})

# Excluir uma obra - DELETE - https://localhost:5000/obra/1


@app.route('/obra/<int:id_obra>', methods=['DELETE'])
@token_obrigatorio
def excluir_obra(autor, id_obra):
    obra_a_ser_excluida = Obra.query.filter_by(
        id_obra=id_obra).first()
    if not obra_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma obra com este id'})
    db.session.delete(obra_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Obra excluída com sucesso!'})


# Consultar todos
@app.route("/autores")
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)

    return jsonify({'autores': lista_de_autores})


# Consultar id
@app.route("/autores/<int:id_autor>", methods=["GET"])
@token_obrigatorio
def obter_autor_por_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify('Autor não encontrado!')
    autor_atual = {}
    autor_atual['id autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify({'autor': autor_atual})

# Criar


@app.route("/autores", methods=["POST"])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor['nome'], email=novo_autor['email'], senha=novo_autor['senha'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso'}, 200)

# Editar


@app.route("/autores/<int:id_autor>", methods=["PUT"])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'mensagem': 'Este usuário não foi encontrado.'})
    try:
        if usuario_a_alterar['nome']:
            autor.nome = usuario_a_alterar['nome']
    except Exception:
        pass

    try:
        if usuario_a_alterar['email']:
            autor.email = usuario_a_alterar['email']
    except Exception:
        pass

    try:
        if usuario_a_alterar['senha']:
            autor.senha = usuario_a_alterar['senha']
    except Exception:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Usuário alterado com sucesso!'}, 200)
# Excluir


@app.route("/autores/<int:id_autor>", methods=["DELETE"])
@token_obrigatorio
def excluir_novel(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor não foi encontrado.'})
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})


app.run(port=5000, host="localhost", debug=True)

# Para rodar localmente e possa ser
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True)
