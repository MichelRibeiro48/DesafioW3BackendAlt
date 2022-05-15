from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json

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
class Transacao(db.Model):
  codTransacao = db.Column(db.Integer, primary_key= True)
  DescTransacao = db.Column(db.String(200))
  NaturezaTransacao = db.Column(db.String(10))

  def to_json(self):
    return {
    "codTransacao": self.codTransacao,
    "DescTransacao": self.DescTransacao,
    "NaturezaTransacao": self.NaturezaTransacao}

class LogTransacoes(db.Model):
  CodTransacao = db.Column(db.Integer, primary_key= True)
  DataTransacoes = db.Column(db.DateTime)
  agencia = db.Column(db.Integer)
  CodContaCorrente = db.Column(db.Integer)
  ValorTransacao = db.Column(db.Float)
  def to_json(self):
    return {
      "DataTransacoes": self.DataTransacoes,
      "CodTransacao": self.CodTransacao, 
      "agencia": self.agencia,
      "CodContaCorrente": self.CodContaCorrente,
      "ValorTransacao": self.ValorTransacao,
      }

def func_response(status, content_name, content, message=False):
  body = {}
  body[content_name] = content

  if(message):
    body["message"] = message
    
  return Response(json.dumps(body), status=status, mimetype="application/json")

@app.route("/cliente/consulta", methods=["GET"])
def ConsultarSaldo():
  body = request.get_json()
  try:
    usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
    usuario_json = usuario.to_json()

    return func_response(200, "usuario", usuario_json, "ok")
  except Exception as e:
    print(e)
    return func_response(400, "usuario", {}, "Usuario inexistente")

@app.route("/cliente/deposito", methods=["PATCH"])
def DepositarConta():
  body = request.get_json()
  try:
    usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
    usuario.saldo += body["ValorDeposito"]
    usuario_json = usuario.to_json()
    db.session.commit()
    return func_response(200, "usuario", usuario_json, "depositado com sucesso")
  except Exception as e:
    print(e)
    return func_response(400, "usuario", {}, "Usuario inexistente")
@app.route("/cliente/saque", methods=["PATCH"])
def SacarConta():
  body = request.get_json()
  try:
    usuario = ContaCorrente.query.filter_by(agencia=body["agencia"], numero=body["numero"]).first()
    valorSaque = body["ValorSaque"]
    if valorSaque > usuario.saldo:
      return func_response(400, "usuario", {}, "Saldo insuficiente")
    usuario.saldo -= valorSaque
    usuario_json = usuario.to_json()
    db.session.commit()
    return func_response(200, "usuario", usuario_json, "Saque realizado com sucesso")
  except Exception as e:
    print(e)
    return func_response(400, "usuario", {}, "Usuario inexistente")
app.run()



