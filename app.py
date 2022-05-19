from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senhasecreta123@db.xfzdbuxmtmaltnmjcceb.supabase.co:5432/postgres'

db = SQLAlchemy(app)

class ContaCorrente(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  numero = db.Column(db.Integer)
  agencia = db.Column(db.Integer)
  saldo = db.Column(db.Float)

  def to_json(self):
    return {"numero": self.numero, "agencia": self.agencia, "saldo": self.saldo, "id": self.id}

class LogTransacoes(db.Model):
  CodTransacao = db.Column(db.Integer, primary_key= True)
  DataTransacoes = db.Column(db.DateTime)
  agencia = db.Column(db.Integer)
  CodContaCorrente = db.Column(db.Integer)
  ValorTransacao = db.Column(db.Float)
  NaturezaTransacao = db.Column(db.String(10))

  def to_json(self):
    return {
      "DataTransacoes": self.DataTransacoes,
      "CodTransacao": self.CodTransacao, 
      "agencia": self.agencia,
      "CodContaCorrente": self.CodContaCorrente,
      "ValorTransacao": self.ValorTransacao,
      "NaturezaTransacao": self.NaturezaTransacao
      }

def func_response(status, content_name, content, message=False):
  body = {}
  body[content_name] = content

  if(message):
    body["message"] = message
    
  return Response(json.dumps(body), status=status, mimetype="application/json")

def ValidarConta(body):
  if ContaCorrente.query.filter_by(agencia=body["agencia"]).first() == None:
    return func_response(400, "usuario", {}, "Agencia Inexistente")
  
  if ContaCorrente.query.filter_by(numero=body["numero"]).first() == None:
    return func_response(400, "usuario", {}, "Numero Inexistente")
    

@app.route("/cliente/consulta", methods=["GET"])
def ConsultarSaldo():
  body = request.get_json()
  if ValidarConta(body) != None:
    return ValidarConta(body)
  
  usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
  usuario_json = usuario.to_json()

  return func_response(302, "usuario", usuario_json, "Consulta realizada com sucesso")

@app.route("/cliente/deposito", methods=["POST"])
def DepositarConta():
  body = request.get_json()
  if ValidarConta(body) != None:
    return ValidarConta(body)

  usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
  usuario.saldo += body["Valor"]
  usuario_json = usuario.to_json()

  novoLog = LogTransacoes(DataTransacoes=datetime.datetime.now(),agencia=usuario.agencia, CodContaCorrente=usuario.numero, ValorTransacao=body["Valor"], NaturezaTransacao="+")
  db.session.add(novoLog)
  db.session.commit()

  return func_response(200, "usuario", usuario_json, "depositado com sucesso")
@app.route("/cliente/saque", methods=["POST"])
def SacarConta():
  body = request.get_json()
  if ValidarConta(body) != None:
    return ValidarConta(body)
  
  usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
  valorSaque = body["Valor"]

  if valorSaque > usuario.saldo:
    return func_response(400, "usuario", {}, "Saldo insuficiente")
  usuario.saldo -= valorSaque
  usuario_json = usuario.to_json()

  novoLog = LogTransacoes(DataTransacoes=datetime.datetime.now(),agencia=usuario.agencia, CodContaCorrente=usuario.numero, ValorTransacao=body["Valor"] * -1, NaturezaTransacao="-")
  db.session.add(novoLog)
  db.session.commit()

  return func_response(200, "usuario", usuario_json, "Saque realizado com sucesso")
app.run()