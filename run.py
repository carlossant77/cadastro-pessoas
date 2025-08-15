from flask import Flask, render_template, redirect, request, session
from datetime import datetime
import sqlite3
import os
import requests

app = Flask(__name__)

app.config['UPLOAD'] = 'static/assets/'

nome_usuario = None

app.secret_key = 'chave_para_usar_flask'

@app.route('/')
def index():
    return render_template ("index.html")

@app.route('/cadastro')
def cadastro():

    return render_template ('cadastro.html')

@app.route('/cliente')
def cliente():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario == None:
        return redirect('/')    

    return render_template ('cadastro_cliente.html', nome_usuario=nome_usuario, foto_perfil=foto_perfil)

@app.route('/fornecedor')
def fornecedor():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario == None:
        return redirect('/')

    return render_template ('cadastro_fornecedor.html', nome_usuario=nome_usuario, foto_perfil=foto_perfil)

@app.route('/logout')
def logoff():

    session.pop('nome_usuario', None)
    session.pop('foto_perfil', None)

    return redirect('/')

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    
    usuario = request.form['usuario']
    senha = request.form['senha']
    nome = request.form['nome']
    imagem = request.files.get('imagem')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT usuario FROM tb_login WHERE usuario = ?', (usuario,))
    usuario_existente = cursor.fetchone()

    if usuario_existente:
            conexao.close()
            return render_template('cadastro.html', erro="O nome de usuário já está em uso!")

    nome_imagem = None
    if imagem and imagem.filename:
        extensao = imagem.filename.split('.')[-1]
        nome_imagem = f"{nome.strip().lower().replace(' ', '_')}.{extensao}"
        caminho_imagem = os.path.join(app.config['UPLOAD'], nome_imagem)
        imagem.save(caminho_imagem)

    if not nome_imagem:
        conexao.close()
        return render_template('cadastro.html', erro="Nenhuma imagem selecionada.")

    with sqlite3.connect('models/dupla.db') as conexao:
        cursor = conexao.cursor()

    sql = 'INSERT INTO tb_login (usuario, senha, nome, imagem) VALUES (?, ?, ?, ?)'
    cursor.execute(sql, (usuario, senha, nome, nome_imagem))

    conexao.commit()
    conexao.close()

    return render_template ('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    usuario = request.form['usuario']
    senha = request.form['senha']

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    sql = "SELECT * from tb_login WHERE usuario=? AND senha=?"
    cursor.execute(sql, (usuario, senha))

    login_usuario = cursor.fetchone()

    if login_usuario:
        session['nome_usuario'] = login_usuario[3]
        session['foto_perfil'] = login_usuario[4]   
        return redirect('/inicio')
    else:
        return redirect('/')

@app.route('/inicio')
def inicio():
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario == None:
        return redirect('/')

    return render_template("inicio.html", nome_usuario=nome_usuario, foto_perfil=foto_perfil)

@app.route('/consulta_clientes')
def consulta(): 

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')
    
    if nome_usuario == None:
        return redirect('/')
    
    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()
 
    sql = 'SELECT * FROM tb_clientes'
    cursor.execute(sql)
    clientes = cursor.fetchall()
 
    conexao.close()

    return render_template ('consulta_cliente.html', clientes=clientes, nome_usuario=nome_usuario, foto_perfil=foto_perfil)


@app.route('/cadastrar_cliente', methods=['POST'])
def cadastrar_cliente():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario == None:
        return redirect('/')

    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    cpf = request.form['cpf']
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    rua = request.form['rua']
    numero = request.form['numero']
    cidade = request.form['cidade']
    estado = request.form['estado']
    cep = request.form['cep']


    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    with sqlite3.connect('models/dupla.db') as conexao:
        cursor = conexao.cursor()

    sql = 'INSERT INTO tb_clientes (nome, email, telefone, cpf, data_cadastro, rua, numero, cidade, estado, cep) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(sql, (nome, email, telefone, cpf, data_cadastro, rua, numero, cidade, estado, cep))

    conexao.commit()
    conexao.close

    return render_template('cadastro_cliente.html', cep=cep, rua=rua, cidade=cidade, estado=estado, nome_usuario=nome_usuario, foto_perfil=foto_perfil)  

@app.route('/buscar_endereco', methods=['GET', 'POST'])
def buscar_endereco():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')
    
    if nome_usuario == None:
        return redirect('/')

    cep, rua, cidade, estado = '', '', '', ''

    site_fonte = request.form['site_fonte']

    cep_busca = request.form.get('cep_busca')
    
    if request.method == 'POST':
        cep_busca = request.form.get('cep_busca', '').replace("-", "").replace(".", "").replace(" ", "")
        print(f"Recebido CEP: {cep_busca}")
        
        if len(cep_busca) == 8:
            link = f'https://viacep.com.br/ws/{cep_busca}/json/'
            requisicao = requests.get(link)
            
            if requisicao.status_code == 200:
                dic_requisicao = requisicao.json()
                rua = dic_requisicao.get('logradouro', '')
                estado = dic_requisicao.get('uf', '')
                cidade = dic_requisicao.get('localidade', '')
    
    return render_template(site_fonte, cep=cep_busca, rua=rua, cidade=cidade, estado=estado, nome_usuario=nome_usuario, foto_perfil=foto_perfil)

@app.route('/consulta_fornecedor')
def consulta_fornecedor(): 

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')
    
    if nome_usuario == None:
        return redirect('/')
    
    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()
 
    sql = 'SELECT * FROM tb_fornecedor'
    cursor.execute(sql)
    fornecedores = cursor.fetchall()
 
    conexao.close()

    return render_template ('consulta_fornecedor.html', fornecedores=fornecedores, nome_usuario=nome_usuario, foto_perfil=foto_perfil)  

@app.route('/cadastrar_fornecedor', methods=['GET', 'POST'])
def cadastrar_fornecedor():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario == None:
        return redirect('/')
    
    nome = request.form['nomef']
    email = request.form['emailf']
    telefone = request.form['telefonef']
    site = request.form['site']
    cnpj = request.form['cnpj']
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    rua = request.form['ruaf']
    numero = request.form['numerof']
    cidade = request.form['cidadef']
    estado = request.form['estadof']
    cep = request.form['cepf']
    
    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    with sqlite3.connect('models/dupla.db') as conexao:
        cursor = conexao.cursor()

    sql = 'INSERT INTO tb_fornecedor (nome, email, telefone, site, cnpj, data_cadastro, rua, numero, cidade, estado, cep) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(sql, (nome, email, telefone, site, cnpj, data_cadastro, rua, numero, cidade, estado, cep))

    conexao.commit()
    conexao.close()

    return render_template('cadastro_fornecedor.html' , cep=cep, rua=rua, cidade=cidade, estado=estado, nome_usuario=nome_usuario, foto_perfil=foto_perfil) 

@app.route('/editar_cliente/<int:clientes_id>', methods=['GET', 'POST'])
def editar_cliente(clientes_id):
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    if request.method == 'POST':
        # Captura os dados do formulário para atualização
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        rua = request.form['rua']
        numero = request.form['numero']
        cidade = request.form['cidade']
        cep = request.form['cep']

        # Atualiza os dados no banco de dados
        sql = '''UPDATE tb_clientes
                 SET nome=?, email=?, telefone=?, cpf=?, rua=?, numero=?, cidade=?, cep=?
                 WHERE clientes_id=?'''
        cursor.execute(sql, (nome, email, telefone, cpf, rua, numero, cidade, cep, clientes_id))
        conexao.commit()

        return redirect('/consulta_clientes')
    else:
        # Busca os dados atuais do cliente para exibir no formulário de edição
        cursor.execute('SELECT * FROM tb_clientes WHERE clientes_id=?', (clientes_id,))
        cliente = cursor.fetchone()
        conexao.close()
        return render_template('editar_cliente.html', cliente=cliente, nome_usuario=nome_usuario, foto_perfil=foto_perfil)
    
@app.route('/excluir_cliente/<int:clientes_id>', methods=['GET', 'POST'])
def excluir_cliente(clientes_id):
    nome_usuario = session.get('nome_usuario')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    # Deleta o cliente do banco de dados
    cursor.execute('DELETE FROM tb_clientes WHERE clientes_id=?', (clientes_id,))
    conexao.commit()
    conexao.close()

    return redirect('/consulta_clientes')

@app.route('/ver_mais_cliente/<int:clientes_id>', methods=['GET'])
def ver_mais_cliente(clientes_id):
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    # Busca os dados do cliente
    cursor.execute('SELECT * FROM tb_clientes WHERE clientes_id=?', (clientes_id,))
    cliente = cursor.fetchone()
    conexao.close()

    if cliente:
        return render_template('ver_cliente.html', cliente=cliente, nome_usuario=nome_usuario, foto_perfil=foto_perfil)
    else:
        return redirect('/consulta_clientes')  # Redireciona caso não encontre o cliente

@app.route('/editar_fornecedor/<int:fornecedor_id>', methods=['GET', 'POST'])
def editar_fornecedor(fornecedor_id):
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    if request.method == 'POST':
        # Captura os dados do formulário para atualização
        nome = request.form['nomef']
        email = request.form['emailf']
        telefone = request.form['telefonef']
        site = request.form['site']
        cnpj = request.form['cnpj']
        rua = request.form['ruaf']
        numero = request.form['numerof']
        cidade = request.form['cidadef']
        estado = request.form['estadof']
        cep = request.form['cepf']

        # Atualiza os dados no banco de dados
        sql = '''UPDATE tb_fornecedor
                 SET nome=?, email=?, telefone=?, site=?, cnpj=?, rua=?, numero=?, cidade=?, estado=?, cep=?
                 WHERE fornecedor_id=?'''
        cursor.execute(sql, (nome, email, telefone, site, cnpj, rua, numero, cidade, estado, cep, fornecedor_id))
        conexao.commit()

        return redirect('/consulta_fornecedor')
    else:
        # Busca os dados atuais do fornecedor para exibir no formulário de edição
        cursor.execute('SELECT * FROM tb_fornecedor WHERE fornecedor_id=?', (fornecedor_id,))
        fornecedor = cursor.fetchone()
        conexao.close()
        return render_template('editar_fornecedor.html', fornecedor=fornecedor, nome_usuario=nome_usuario, foto_perfil=foto_perfil)
    
@app.route('/excluir_fornecedor/<int:fornecedor_id>', methods=['GET', 'POST'])
def excluir_fornecedor(fornecedor_id):
    nome_usuario = session.get('nome_usuario')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    # Deleta o fornecedor do banco de dados
    cursor.execute('DELETE FROM tb_fornecedor WHERE fornecedor_id=?', (fornecedor_id,))
    conexao.commit()
    conexao.close()

    return redirect('/consulta_fornecedor')

@app.route('/ver_mais_fornecedor/<int:fornecedor_id>', methods=['GET'])
def ver_mais_fornecedor(fornecedor_id):
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    # Busca os dados do fornecedor
    cursor.execute('SELECT * FROM tb_fornecedor WHERE fornecedor_id=?', (fornecedor_id,))
    fornecedor = cursor.fetchone()
    conexao.close()

    if fornecedor:
        return render_template('ver_fornecedor.html', fornecedor=fornecedor, nome_usuario=nome_usuario, foto_perfil=foto_perfil)
    else:
        return redirect('/consulta_fornecedor')  # Redireciona caso não encontre o fornecedor
    
@app.route('/gerenciar_contas')
def gerenciar_contas():

    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')
    
    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()
 
    sql = 'SELECT * FROM tb_login'
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    
    conexao.close()

    return render_template ('gerenciar_contas.html', nome_usuario=nome_usuario, foto_perfil=foto_perfil, usuarios=usuarios)

@app.route('/editar_conta/<int:usuario_id>', methods=['GET', 'POST'])
def editar_conta(usuario_id):
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    if request.method == 'POST':
        # Captura os dados do formulário para atualização
        nome = request.form['nome']
        usuario = request.form['usuario']

        # Atualiza os dados no banco de dados
        sql = '''UPDATE tb_login
                 SET nome=?, usuario=?
                 WHERE usuario_id=?'''
        cursor.execute(sql, (nome, usuario, usuario_id))
        conexao.commit()

        return redirect('/gerenciar_contas')
    else:
        # Busca os dados atuais do login para exibir no formulário de edição
        cursor.execute('SELECT * FROM tb_login WHERE usuario_id=?', (usuario_id,))
        login = cursor.fetchone()
        conexao.close()
        return render_template('editar_conta.html', login=login, nome_usuario=nome_usuario, foto_perfil=foto_perfil)
    
@app.route('/excluir_conta/<int:usuario_id>', methods=['GET', 'POST'])
def excluir_conta(usuario_id):
    
    conexao = sqlite3.connect('models/dupla.db')
    cursor = conexao.cursor()

    # Deleta o login do banco de dados
    cursor.execute('DELETE FROM tb_login WHERE usuario_id=?', (usuario_id,))
    conexao.commit()
    conexao.close()

    return redirect('/gerenciar_contas')

@app.route('/cadastrar_conta', methods=['GET', 'POST'])
def cadastrar_conta():
    nome_usuario = session.get('nome_usuario')
    foto_perfil = session.get('foto_perfil')

    if nome_usuario is None:
        return redirect('/')

    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']
        imagem = request.files.get('imagem')

        conexao = sqlite3.connect('models/dupla.db')
        cursor = conexao.cursor()

        cursor.execute('SELECT usuario FROM tb_login WHERE usuario = ?', (usuario,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
                conexao.close()
                return render_template('cadastro.html', erro="O nome de usuário já está em uso!")

        nome_imagem = None
        if imagem and imagem.filename:
            extensao = imagem.filename.split('.')[-1]
            nome_imagem = f"{nome.strip().lower().replace(' ', '_')}.{extensao}"
            caminho_imagem = os.path.join(app.config['UPLOAD'], nome_imagem)
            imagem.save(caminho_imagem)

        if not nome_imagem:
            conexao.close()
            return render_template('cadastro.html', erro="Nenhuma imagem selecionada.")

        with sqlite3.connect('models/dupla.db') as conexao:
            cursor = conexao.cursor()

        sql = 'INSERT INTO tb_login (usuario, senha, nome, imagem) VALUES (?, ?, ?, ?)'
        cursor.execute(sql, (usuario, senha, nome, nome_imagem))

        conexao.commit()
        conexao.close()

        return redirect('/gerenciar_contas')

    return render_template('cadastrar_conta.html', nome_usuario=nome_usuario, foto_perfil=foto_perfil)

app.run(host='127.0.0.1', port=80, debug=True)

