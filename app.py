import re
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, url_for, flash, redirect
from flask.typing import TemplateFilterCallable
from sqlalchemy.orm import backref
from sqlalchemy import column, text
from werkzeug.datastructures import ContentRange
from werkzeug.exceptions import MethodNotAllowed, abort
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
import os, datetime

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JcCwEUu3ZLzQc96'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
db = SQLAlchemy(app)

# Definicao das tabelas do banco de dados
class funcionarios(db.Model):
    func_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    func_nome = db.Column(db.String(45), nullable=False)
    func_cargo = db.Column(db.String(45), nullable=False)
    func_username = db.Column(db.String(20), nullable=False)
    func_password = db.Column(db.String(45), nullable=False)
    func_obs = db.Column(db.String(150))

class turmas(db.Model):
    trm_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    trm_ativo = db.Column(db.Boolean,default=True)
    trm_cod_prof = db.Column(db.Integer, nullable=False)
    trm_horario = db.Column(db.String(45))
    trm_obs = db.Column(db.String(150))

class alunos(db.Model):   # Nome da tabela e campos conforme banco de dados
    aln_id = db.Column(db.Integer, primary_key=True) # RA do aluno
    aln_nome = db.Column(db.String(45), nullable=False)
    aln_matriculado = db.Column(db.Boolean,default=True)
    aln_serie = db.Column(db.Integer, nullable=False)
    aln_turma = db.Column(db.Integer, nullable=False)
    aln_nivel = db.Column(db.Integer, nullable=False)
    aln_email_resp = db.Column(db.String(45))
    aln_obs = db.Column(db.String(150))
    # aln_turma = db.relationship('historicos', backref='fp_fornNome') #Nome da Classe e campo virtual

""" class historicos(db.Model):
    fp_forn = db.Column(db.Integer, db.ForeignKey('funcionarios.aln_id'), primary_key=True, nullable=False)
    fp_codforn = db.Column(db.String(20), primary_key=True, nullable=False)
    fp_descricao = db.Column(db.String(50), nullable=False)
    fp_modelo = db.Column(db.String(30))
    fp_trm = db.Column(db.String(20), nullable=False)
    fp_obs = db.Column(db.String(150)) """

class historicos(db.Model):
    hst_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hst_cod_aln=db.Column(db.Integer,nullable=False)
    hst_nv_ant=db.Column(db.Integer,nullable=False)
    hst_nv_atual=db.Column(db.Integer,nullable=False)
    hst_data_alt = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    hst_cod_alt=db.Column(db.Integer,nullable=False)
    hst_cod_aprov=db.Column(db.Integer,nullable=False)
    hst_trm_ant=db.Column(db.Integer,nullable=False)
    hst_trm_atual=db.Column(db.Integer,nullable=False)
    hst_obs = db.Column(db.String(150))

# Rotinas de CRUD
def get_post_func(id):
    reg_func = funcionarios.query.filter_by(func_id=id).first()
    if reg_func is None:
        flash('Colaborador(a) não cadastrado(a)')
    return reg_func

def get_post_trm(id):
    reg_trm = turmas.query.filter_by(trm_id=id).first()
    if reg_trm is None:
        flash('turma não cadastrada')
    return reg_trm

def get_post_aln(id):
    reg_aln = alunos.query.filter_by(aln_id=id).first()
    if reg_aln is None:
        flash('Aluno(a) nâo cadastrado')
    return reg_aln

def get_post_hst(id):
    reg_hst = historicos.query.filter_by(hst_id = id).first()
    if reg_hst is None:
        abort(404)
    return reg_hst

def atualiza_saldo(codProd, wsQuant, wsTipo):
    ws_RegProd = get_post_trm(codProd)
    ws_SaldoProd = float(ws_RegProd.trm_saldo)
    if wsTipo == "E":
        ws_SaldoProd += wsQuant
    else:
        if (ws_SaldoProd < wsQuant):
            flash('Quantidade maior que saldo atual')
            return False
        else:
            ws_SaldoProd -= wsQuant
    ws_RegProd.trm_saldo = ws_SaldoProd
    db.session.commit()
    return True

def verifica_saldo(codProd, wsQuantNova, wsQuantAtual, wsTipo):
    ws_RegProd = get_post_trm(codProd)
    ws_SaldoProd = float(ws_RegProd.trm_saldo)
    ws_Qtde = wsQuantNova - wsQuantAtual
    if wsTipo == "E":
        ws_SaldoProd += ws_Qtde
        if ws_SaldoProd < 0:
            flash('Quantide maior que saldo atual')
            return False
    else:
        ws_SaldoProd -= ws_Qtde
        if (ws_SaldoProd < 0):
            flash('Quantidade maior que saldo atual')
            return False
    return True

# Definicao de rotas
@app.route('/')
def index():
    return render_template('index.html')

# Definição dos menus
@app.route('/mnucadastro')
def mnucadastro():
    return render_template('Menus/mnucadastro.html')

@app.route('/mnurelatorios')
def mnurelatorios():
    return render_template('Menus/mnurelatorios.html')

# Encaminhamento para os fomulários




# ----------------- Funcionários ---------------------------

@app.route('/mnucadastro/funcionarios')   # obrigatório ter o parametro no endereco
def cad_funcionarios():
    lista_func = funcionarios.query.all()
    return render_template('funcionarios/funcionarios.html',lista_func=lista_func)

@app.route('/mnucadastro/lstfunc', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_func():
    if request.method == 'POST':
        dado = request.form['form_nome']
        lista_func = funcionarios.query.filter(funcionarios.func_nome.like(dado + "%")) # filter_by somente um linha de retorno
        return render_template('funcionarios/funcionarios.html',lista_func=lista_func)
    else:
        return render_template('funcionarios/lstfunc.html')

@app.route('/mnucadastro/colab_inc', methods=('GET', 'POST'))
def inc_func():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_Nome = request.form['form_nome']
        ws_Cargo = request.form['form_cargo']
        ws_Username=request.form['form_username']
        ws_Senha=request.form['form_senha']
        ws_Obs = request.form['form_obs']
        if not ws_Nome:
            flash('O nome é obrigatório')
        else:
            reg_func = funcionarios(func_nome=ws_Nome,func_cargo=ws_Cargo,func_username=ws_Username,func_password=ws_Senha, func_obs=ws_Obs)
            db.session.add(reg_func)
            db.session.commit()
            flash('Inclusao feita com sucesso')
        return redirect(url_for('cad_funcionarios'))
    return render_template('funcionarios/incfunc.html')

@app.route('/mnucadastro/<int:id>/colab_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_func(id):
    reg_func = get_post_func(id)
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_cargo = request.form['form_cargo']
        ws_username = request.form['form_username']
        ws_password = request.form['form_senha']
        ws_obs = request.form['form_obs']
        if not ws_nome:
            flash('Nome e obrigatório','error')
        else:
            reg_func.func_nome = ws_nome
            reg_func.func_cargo = ws_cargo
            reg_func.func_username = ws_username
            reg_func.func_password = ws_password
            reg_func.func_obs = ws_obs
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_funcionarios'))
    return render_template('funcionarios/altfunc.html', funcionarios=reg_func)

@app.route('/mnucadastro/<int:id>/colab_del', methods=('GET', 'POST'))
def del_func(id):
    reg_func = get_post_func(id)
    db.session.delete(reg_func)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_func.func_nome))
    return redirect(url_for('cad_funcionarios'))


# --------------------- Turmas --------------------------

@app.route('/mnucadastro/turmas', methods=('GET', 'POST'))
def cad_turmas():
    lista_trm = turmas.query.all()
    return render_template('turmas/turmas.html', lista_trm=lista_trm)

#        ws_nom_prof = get_post_func(ws_for)

@app.route('/mnucadastro/turmas/lsttrm', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_trm():
    if request.method == 'POST':
        dado = request.form['form_cod_prof']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_trm = turmas.query.filter(turmas.trm_cod_prof.like(dado + "%")) # filter_by somente um linha de retorno
        return render_template('turmas/turmas.html',lista_trm=lista_trm)
    else:
        return render_template('turmas/lsttrm.html')

@app.route('/mnucadastro/<string:id>/trm_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_trm(id):
    reg_trm = get_post_trm(id)
    if request.method == 'POST':
        #ws_ativo = request.form['form_ativo']
        ws_ativo=True
        ws_cod_prof = request.form['form_cod_prof']
        ws_horario = request.form['form_horario']
        ws_obs = request.form['form_obs']
        if not ws_cod_prof:
            flash('Código do professor é obrigatório')
        else:
            reg_trm.trm_ativo = ws_ativo
            reg_trm.trm_cod_prof = ws_cod_prof
            reg_trm.trm_horario = ws_horario
            reg_trm.trm_obs = ws_obs
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_turmas'))
    return render_template('turmas/alttrm.html', turmas=reg_trm)

@app.route('/mnucadastro/trm_inc', methods=('GET', 'POST'))
def inc_trm():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_ativo = request.form.get('form_ativo')
        if (ws_ativo == 'on'):
            ws_ativo = True
        else:
            ws_ativo = False
        ws_cod_prof = request.form['form_cod_prof']
        ws_horario = request.form['form_horario']
        ws_obs = request.form['form_obs']
        if not ws_cod_prof:
            flash('Código do professor(a) é obrigatorio')
        else:
            reg_trm = turmas(trm_ativo=ws_ativo,trm_cod_prof=ws_cod_prof,trm_horario=ws_horario,trm_obs=ws_obs)
            db.session.add(reg_trm)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_turmas'))
    return render_template('turmas/inctrm.html')

@app.route('/mnucadastro/<string:id>/trm_del', methods=('GET', 'POST'))
def del_trm(id):
    reg_trm = get_post_trm(id)
    db.session.delete(reg_trm)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_trm.trm_id))
    return redirect(url_for('cad_turmas'))

# -------------------- Alunos --------------------------------

@app.route('/mnucadastro/alunos', methods=('GET', 'POST'))
def cad_alunos():
    lista_aln = alunos.query.all()
    return render_template('alunos/alunos.html', lista_aln=lista_aln)

@app.route('/mnucadastro/lstaln', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_aln():
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_turma = request.form['form_turma']
        ws_nivel = request.form['form_nivel']
        ws_flag = 0
        ws_filtro = ""
        if ws_nome:
            ws_filtro = 'alunos.aln_nome like "'+ws_nome+'%"'
            ws_flag = 1
        if ws_turma:
            if ws_flag == 1:
                ws_filtro = ws_filtro + ' and '
            ws_filtro = ws_filtro + ' alunos.aln_turma = '+ws_turma
            ws_flag = 1
        if ws_nivel:
            if ws_flag == 1:
                ws_filtro = ws_filtro + ' and '
            ws_filtro = ws_filtro + ' alunos.aln_nivel = '+ws_nivel
            ws_flag = 1
        lista_aln = alunos.query.filter(text(ws_filtro))# filter_by somente um linha de retorno
        return render_template('alunos/alunos.html',lista_aln=lista_aln)
    else:
        return render_template('alunos/lstaln.html')

@app.route('/mnucadastro/aln_inc', methods=('GET', 'POST'))
def inc_aln():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_id = request.form['form_ra']
        ws_nome = request.form['form_nome']
        ws_serie = request.form['form_serie']
        ws_turma = request.form['form_turma']
        ws_nivel = request.form['form_nivel']
        ws_email_resp = request.form['form_email_resp']
        ws_obs = request.form['form_obs']
        ws_incluir = True
        ws_transf = [0,ws_nivel,0,0,0,ws_turma,"Inclusão do aluno"]
        if  ws_id == "":
            flash('RA é obrigatório')
            ws_incluir = False
        else: 
            if ws_nome is None:
                flash('Nome é obrigatório')
                ws_incluir = False
        if not ws_serie:
            flash('Série é obrigatório')
            ws_incluir = False
        if not ws_nivel:
            flash('Nível é obrigatório')
            ws_incluir = False
        ws_Regtrm = get_post_trm(ws_turma)
        if ws_Regtrm is None:
            ws_incluir = False
        if ws_incluir:
            reg_aln = alunos(aln_id=ws_id,aln_nome=ws_nome,aln_serie=ws_serie,aln_turma=ws_turma,aln_nivel=ws_nivel,aln_email_resp=ws_email_resp,
            aln_obs=ws_obs)
            db.session.add(reg_aln)
            db.session.commit()
            ws_status = inc_hst(reg_aln,ws_transf)
            if not ws_status:
                flash("Erro ao incluir o histórico")
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_alunos'))
    return render_template('alunos/incaln.html')

# ws_transf(nv_ant,nv_atual,cod_alt,cod_aprov,trm_ant,trm_atual, obs)


@app.route('/mnucadastro/<int:id>/aln_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_aln(id):
    reg_aln = get_post_aln(id)
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_serie = request.form['form_serie']
        ws_email_resp = request.form['form_email_resp']
        ws_obs = request.form['form_obs']
        ws_alterar = True
        if not ws_nome:
            flash('Nome é obrigatório')
            ws_alterar = False
        if not ws_serie:
            flash('Serie é obrigatório')
            ws_alterar = False
        if ws_alterar:
            reg_aln.aln_nome = ws_nome
            reg_aln.aln_serie = ws_serie
            reg_aln.aln_email_resp = ws_email_resp
            reg_aln.aln_obs = ws_obs
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_alunos'))
    return render_template('alunos/altaln.html', post=reg_aln, alunos = reg_aln)

@app.route('/mnucadastro/<int:id>/aln_del', methods=('GET', 'POST'))
def del_aln(id):
    reg_aln = get_post_aln(id)
    db.session.delete(reg_aln)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_aln.aln_nome))
    return redirect(url_for('cad_alunos'))

# ------------------------- Históricos -----------------------------------

@app.route('/mnurelatorio/lsthst', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_hst():
    if request.method == 'POST':
        ws_ra= request.form['form_ra']                 # Nomes so sao reconhecidos se estiverem dentro do form
        # ws_nome = request.form['form_nome']
        ws_nv_ant = request.form['form_nv_ant']
        ws_nv_atual = request.form['form_nv_atual']
        wsFlag = 0
        ws_Filtro = ''
        if ws_ra :
            ws_Filtro = 'historicos.hst_cod_aln = '+ws_ra
            wsFlag =1
        if ws_nv_ant :
            if wsFlag == 1:
                ws_Filtro = ws_Filtro + ' and '
            ws_Filtro = ws_Filtro + 'historicos.hst_nv_ant = '+ws_nv_ant
            wsFlag = 1
        if ws_nv_atual :
            if wsFlag == 1:
                ws_Filtro = ws_Filtro + ' and '
            ws_Filtro = ws_Filtro + 'historicos.hst_nv_atual = '+ws_nv_atual
            wsFlag = 1
        lista_hst = historicos.query.filter(text(ws_Filtro)) 
        lista_aln = get_post_aln(ws_ra)  
        ws_nome = lista_aln.aln_nome     # filter_by somente um linha de retorno
        return render_template('historicos/lsthst.html',lista_hst=lista_hst,ws_nome=ws_nome)
    else:
        return render_template('historicos/evoaln.html')

def inc_hst(reg_aln,ws_transf):                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    ws_cod_aln = reg_aln.aln_id
    ws_nv_ant = ws_transf[0]
    ws_nv_atual = ws_transf[1]
    ws_cod_alt = ws_transf[2]
    ws_cod_aprov = ws_transf[3]
    ws_trm_ant = ws_transf[4]
    ws_trm_atual = ws_transf[5]
    ws_obs = ws_transf[6]
    reg_hst = historicos(hst_cod_aln=ws_cod_aln,hst_nv_ant=ws_nv_ant,hst_nv_atual=ws_nv_atual,hst_cod_alt=ws_cod_alt,hst_cod_aprov=ws_cod_aprov,hst_trm_ant=ws_trm_ant,hst_trm_atual=ws_trm_atual,hst_obs=ws_obs)
    db.session.add(reg_hst)
    db.session.commit()
    flash('Inclusao feita com sucesso')
    return True
# ws_transf(nv_ant,nv_atual,cod_alt,cod_aprov,trm_ant,trm_atual,obs)
# ---------------------- Relatórios ---------------------------------
@app.route('/mnucadastro/reltrm', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def rel_turmas():
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_turma = request.form['form_turma']
        ws_nivel = request.form['form_nivel']
        ws_flag = 0
        ws_filtro = ""
        if ws_nome:
            ws_filtro = 'alunos.aln_nome like "'+ws_nome+'"*"'
            ws_flag = 1
        if ws_turma:
            if ws_flag == 1:
                ws_filtro = ws_filtro + ' and '
            ws_filtro = ws_filtro + ' alunos.aln_turma = '+ws_turma
            ws_flag = 1
        if ws_nivel:
            if ws_flag == 1:
                ws_filtro = ws_filtro + ' and '
            ws_filtro = ws_filtro + ' alunos.aln_nivel = '+ws_nivel
            ws_flag = 1
        lista_aln = alunos.query.filter(text(ws_filtro))# filter_by somente um linha de retorno
        return render_template('alunos/alunos.html',lista_aln=lista_aln)
    else:
        return render_template('alunos/lstaln.html')

# ----------------- Mudanças ---------------------------------

# -------------- Turma --------------------------
@app.route('/mnucadastro/mudtrm', methods=('GET', 'POST'))
def mudanca_trm():
    lista_aln = alunos.query.all()
    return render_template('mudancas/mudtrm.html', lista_aln=lista_aln)

@app.route('/mnucadastro/<int:id>/alt_mudtrm', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_mudtrm(id):
    reg_aln = get_post_aln(id)
    if request.method == 'POST':
        ws_trm_atual = request.form['form_trm_atual']
        ws_trm_ant = reg_aln.aln_turma
        ws_nivel = reg_aln.aln_nivel
        ws_transf = [ws_nivel,ws_nivel,0,0,ws_trm_ant,ws_trm_atual,"Mudança de turma"]
        ws_status = inc_hst(reg_aln,ws_transf)
        reg_aln.aln_turma = ws_trm_atual
        db.session.commit()
        if not ws_status:
            flash('Erro ao incluir histórico')
        return redirect(url_for('mudanca_trm'))
    return render_template('mudancas/alt_mudtrm.html', alunos=reg_aln)

# --------------------- Nível --------------------------
@app.route('/mnucadastro/mudnv', methods=('GET', 'POST'))
def mudanca_nv():
    lista_aln = alunos.query.all()
    return render_template('mudancas/mudnv.html', lista_aln=lista_aln)

@app.route('/mnucadastro/<int:id>/alt_mudnv', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_mudnv(id):
    reg_aln = get_post_aln(id)
    if request.method == 'POST':
        ws_nv_atual = request.form['form_nv_atual']
        ws_nv_ant = reg_aln.aln_turma
        ws_turma = reg_aln.aln_turma
        ws_transf = [ws_nv_ant,ws_nv_atual,0,0,ws_turma,ws_turma,"Mudança de nível"]
        ws_status = inc_hst(reg_aln,ws_transf)
        reg_aln.aln_nivel = ws_nv_atual
        db.session.commit()
        if not ws_status:
            flash('Erro ao incluir histórico')
        return redirect(url_for('mudanca_nv'))
    return render_template('mudancas/alt_mudnv.html', alunos=reg_aln)

# ------------------- Análise estatística ------------------
@app.route('/mnurelatorio/lstniv', methods=('GET','POST'))   # Nao esquecer de colocar os metodos aceitos
def aln_niv():
    con = sqlite3.connect('database.db')
    df = pd.read_sql_query("select aln_nivel as nivel, count(*) as total from alunos group by aln_nivel",con)
    print(df.head())
    wsTab=df[['nivel','total']]
    print(wsTab)
    ws_lista=[wsTab.to_html(col_space=250,classes='data')]
    #x = df['aln_nivel']
    #y = df['total']
    #plt.figure(figsize=(10,5))
    #plt.plot(x,y,'o',label="Dados originais")
    #plt.legend()
    #plt.xlabel("x")
    #plt.ylabel("y")
    #plt.grid()
    con.close()
    return render_template('relatorios/lstniv.html', list_nivel=ws_lista)

@app.route('/mnurelatorio/lstalntrm', methods=('GET','POST'))   # Nao esquecer de colocar os metodos aceitos
def aln_trm():
    con = sqlite3.connect('database.db')
    df = pd.read_sql_query("select aln_turma as turma, aln_nivel as nivel, aln_id as total from alunos",con)
    wsTab=df[['turma','nivel','total']]
    wsGroupNivel=wsTab.groupby(['turma','nivel'])['total'].count()
    print(wsGroupNivel)
    ws_serie_df = wsGroupNivel.to_frame()
    ws_lista=[ws_serie_df.to_html(col_space=250,classes='data')]
    con.close()
    return render_template('relatorios/lstalntrm.html', list_trm=ws_lista)
