from flask import Flask,render_template,request,redirect,flash,g
from flask_login import login_required, current_user, login_user, logout_user, url_for
from models import UserModel,db,login
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'xyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

app.config.update(dict(
    SECRET_KEY='bardzosekretnawartosc',
    DATABASE=os.path.join(app.root_path, 'db.sqlite'),
))


@app.before_first_request
def create_all():
    db.create_all()
    

     
@app.route('/blogs')
def blog():
    return render_template('zadania.html')

@app.route('/gumbo')
def gumbo():
    dane = {'tytul':'Przepis na Gumbo', 'tresc':'Gumbo z Nowego Orleanu. Garnek pełen smaku'}
    return render_template('gumbo.html',tytul=dane['tytul'],tresc=dane['tresc'])


@app.route('/jambalaya')
def jambalaya():
    dane = {'tytul':'Przepis na Kreolską Jambalaya', 'tresc':'Daleka krewna paelli'}
    return render_template('Jambalaya.html',tytul=dane['tytul'],tresc=dane['tresc'])
 
    """Metoda logowania"""
@app.route('/login', methods = ['POST', 'GET'])
def login():
    dane = {'tytul':'Strona Logowania', 'tresc':'Zaloguj się aby kontynuować'}
   
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and email!='' and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/zadania')
        else:
            return redirect('/blad')
     
    return render_template('login.html',tytul=dane['tytul'],tresc=dane['tresc'])
    
        

@app.errorhandler(401) 
def page_not_found(e): 
    tytul="Komunikat"
    tresc="Coś poszło nie tak..." 
    blad = "401" 
    return render_template('blad.html', tresc=tresc,tytul=tytul, blad=blad)


@app.route('/omnie')
def omnie():
    dane = {'tytul':'Strona o mnie', 'tresc':'Witaj'}
    return render_template('omnie.html',tytul=dane['tytul'],tresc=dane['tresc'])


    """Rejestrowanie nowego uzytkownika"""
@app.route('/register', methods=['POST', 'GET'])
def register():
    dane = {'tytul':'Rejstracja', 'tresc':'Zarejestruj się.'}
    if current_user.is_authenticated:
        return redirect('/blogs')
     
    if request.method == 'POST':
       
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return redirect('/zlyMail')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html',tytul=dane['tytul'],tresc=dane['tresc'])
 
 
@app.route('/zlyMail')
def zlyMail():
    dane = {'tytul':'Nie udało się założyć konta!', 'tresc':' '}
    return render_template('mailZajety.html',tytul=dane['tytul']) 
 
 
 
@app.route('/wyloguj')
def logout():
    dane = {'tytul':'Nastapiło poprawne wylogowanie.', 'tresc':' '}
    logout_user()
    return render_template('wyloguj.html',tytul=dane['tytul'])

    """Strona główna"""
@app.route('/')
def index():
    dane = {'tytul':'Home', 'tresc':'Odkrywaj nowe smaki!'}
    return render_template('index.html',tytul=dane['tytul'],tresc=dane['tresc'])

def get_db():
    """Połączenie  z bazą danych zawierająca posty"""
    if not g.get('db'):  # jeżeli brak połączenia, to je tworzymy
        con = sqlite3.connect(app.config['DATABASE'])
        con.row_factory = sqlite3.Row
        g.db = con  # zapisujemy połączenie w kontekście aplikacji
    return g.db  # zwracamy połączenie z bazą


@app.teardown_appcontext
def close_db(error):
    """Zamykanie połączenia z bazą"""
    if g.get('db'):
        g.db.close()

    """Dodawanie postów"""
@app.route('/zadania', methods=['GET', 'POST'])
@login_required 
def zadania():
    error = None
    if request.method == 'POST':
        
        zadanie = request.form['zadanie'].strip()
        if len(zadanie) > 0:
            
            zrobione = current_user.username
            data_pub = datetime.now()
            db = get_db()
            db.execute('INSERT INTO zadania VALUES (?, ?, ?, ?);',
                       [None, zadanie, zrobione, data_pub])
            db.commit()
            flash('Pomyślnie dodano post.')
            return redirect(url_for('zadania'))

        error = 'Nie możesz dodać pustego postu!'  # komunikat o błędzie

    db = get_db()
    kursor = db.execute('select * from zadania order by data_pub desc;')
    zadania = kursor.fetchall()
    return render_template('zadania.html', zadania=zadania, error=error)

@app.route('/blad')
def blad():
    dane = {'tytul':'Wprowadziłeś błędne dane', 'tresc':'Spróbuj ponownie.'}
    return render_template('blad.html',tytul=dane['tytul'])



if __name__ == "__main__":
    app.run(debug=True)