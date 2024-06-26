from flask import Flask,request,render_template,redirect,session
from flask_sqlalchemy import SQLAlchemy
import time

app=Flask(__name__)
app.secret_key="transactions"

# sqlite database 
# app.config['SQLALCHEMY_DATABASE_URI']="postgresql://utaai4i6bcjecbhcpy7f:9N7FEoLUGnMnS2bF67ABzrvRNoFrKU@bhaugryd6b281f3vgm2c-postgresql.services.clever-cloud.com:50013/bhaugryd6b281f3vgm2c"


# mysql database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ukwtzofo2dd1ktk6:01aAgsJTJsXWAwgxG1T3@bmefhufz3eytgfyziudf-mysql.services.clever-cloud.com:3306/bmefhufz3eytgfyziudf'

app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db=SQLAlchemy(app)
app.app_context().push()

# Models
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    username=db.Column(db.String(30),unique=True,nullable=False)
    balance=db.Column(db.Float,nullable=False)
    password=db.Column(db.String(30),nullable=False)

# class Balance(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(30),nullable=False)
#     username=db.Column(db.String(30),nullable=False)
#     balance=db.Column(db.Integer,nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

# signup
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        username=request.form['username']
        password=request.form['password']
        # print(name,username,password)
        try:
            user=User.query.filter_by(username=username).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user=User.query.filter_by(username=username).first()
        
        if not user:
            if len(name)<=30 and len(username)<=30 and len(password)<=30:

                data=User(name=name,username=username,password=password,balance=0)
                db.session.add(data)
                db.session.commit()
            else:
                return "<center><h1>Please enter valid value</h1></center>"   
        else:
            return "<center><h1>user already present</h1></center>"
    return redirect('/')

@app.route('/signin')
def signin():
    return render_template('signin.html')



@app.route('/userhome',methods=['GET','POST'])
def userhome():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        try:
            user=User.query.filter_by(username=username).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user=User.query.filter_by(username=username).first()
        
        if user:
            if user.password==password:
                session['id']=user.id
                session['username']=user.username
                session['name']=user.name
                session['balance']=user.balance
                return render_template('userhome.html')
            else:
                return "<h1>wrong password</h1>"
        else:
            return "<h1>user not found</h1>"
    return render_template('userhome.html')

@app.route('/credit',methods=['POST','GET'])
def credit():
    if request.method=='POST':
        amount=request.form['amount']
        try:
            user=User.query.filter_by(username=session['username']).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user=User.query.filter_by(username=session['username']).first()
        # print("hello world",user.balance)
        amount=float(amount)
        user.balance=user.balance+amount
        db.session.add(user)
        db.session.commit()
        session['balance']=user.balance
        return redirect('/userhome')
    return render_template('credit.html')

@app.route('/debit',methods=['GET','POST'])
def debit():
    if request.method=='POST':
        amount=request.form['amount']
        amount=float(amount)
        # print(amount)
        try:
            user=User.query.filter_by(username=session['username']).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user=User.query.filter_by(username=session['username']).first()
        if user.balance>0:
            if amount<=user.balance:
                user.balance=user.balance-amount
                db.session.add(user)
                db.session.commit()
                session['balance']=user.balance
                return redirect('/userhome')
            else:
                return "<h1>Entered Amount for debit is greater than your balance</h1>"
        else:
            return "<h1>Sorry your account balance is 0 Crypteon you can't debit<h1>"
    return render_template('debit.html')

@app.route('/transfer',methods=['GET','POST'])
def transfer():
    if request.method=='POST':
        username=request.form['username']
        amount=request.form['amount']
        amount=float(amount)
        try:
            user=User.query.filter_by(username=session['username']).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user=User.query.filter_by(username=session['username']).first()
        try:
            user1=User.query.filter_by(username=username).first()
        except Exception as e:
            db.session.rollback()
            time.sleep(1)
            db.session.begin()
            user1=User.query.filter_by(username=username).first()
        if user1:
            if user.balance>0:
                if amount<=user.balance:
                    user.balance=user.balance-amount
                    db.session.add(user)
                    db.session.commit()
                    session['balance']=user.balance
                    user1.balance=user1.balance+amount
                    db.session.add(user1)
                    db.session.commit()
                    return redirect('/userhome')
                else:
                    return "<h1>Entered amount is greater than your balance</h1>"
            else:
                return "<h1>Sorry your account balance is 0 Crypteon</h1>"
        else:
            return "<h1>Sorry User not found</h1>"
    return render_template('transfer.html')

if __name__=='__main__':
    app.run(debug=True,port=8000)