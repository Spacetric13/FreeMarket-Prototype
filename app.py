from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import sqlite3
import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
bcrypt = Bcrypt(app) # Inicializamos Bcrypt para la seguridad

# Función auxiliar para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('marketplace.db')
    # Permite acceder a las columnas por nombre (ej: fila['correo'])
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def home():
    # Publicaciones falsas para la demo de la Sprint Review
    productos_mock = [
        {"id": 1, "titulo": "Auriculares Inalámbricos Premium", "precio": "$120.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Audio"},
        {"id": 2, "titulo": "Reloj Inteligente FM Series", "precio": "$250.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Smartwatch"},
        {"id": 3, "titulo": "Teclado Mecánico RGB", "precio": "$85.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Teclado"},
        {"id": 4, "titulo": "Monitor 4K 27 Pulgadas", "precio": "$320.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Monitor"},
        {"id": 5, "titulo": "Silla Gamer Ergonómica", "precio": "$180.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Silla+Gamer"},
        {"id": 6, "titulo": "Mouse Inalámbrico Pro", "precio": "$45.000", "imagen": "https://via.placeholder.com/300x200/4A148C/FFC107?text=Mouse"}
    ]
    
    # Obtenemos el nombre si está logueado, sino será None
    nombre_usuario = session.get('nombre')
    
    return render_template('home.html', nombre=nombre_usuario, productos=productos_mock)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # El .strip() elimina espacios en blanco al inicio o final
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip()
        password = request.form['password']
        
        # --- 1. VALIDACIÓN: Nombre y Apellido ---
        # Dividimos el string por espacios. Si hay menos de 2 palabras, falta el apellido.
        if len(nombre.split()) < 2:
            flash('Debes ingresar al menos tu nombre y un apellido.', 'error')
            return render_template('registro.html')
            
        # --- 2. VALIDACIÓN: Contraseña de 8 dígitos ---
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return render_template('registro.html')
            
        # --- 3. VALIDACIÓN: Mezcla de categorías (al menos 2) ---
        categorias_cumplidas = 0
        if re.search(r'[A-Z]', password): categorias_cumplidas += 1 # Mayúsculas
        if re.search(r'[a-z]', password): categorias_cumplidas += 1 # Minúsculas
        if re.search(r'[0-9]', password): categorias_cumplidas += 1 # Números
        if re.search(r'[#$%&]', password): categorias_cumplidas += 1 # Símbolos específicos
        
        if categorias_cumplidas < 2:
            flash('La contraseña debe incluir al menos 2 de los siguientes: mayúsculas, minúsculas, números o símbolos (#$%&).', 'error')
            return render_template('registro.html')
            
        # --- GUARDAR EN BASE DE DATOS ---
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Como es un prototipo simplificado, guardamos "confirmado" como 1 (True) automáticamente
            # para simular que el correo "existe y se verificó" sin tener que hacer el flujo real.
            cursor.execute('''
                INSERT INTO usuarios (nombre, correo, password_hash, confirmado) 
                VALUES (?, ?, ?, 1)
            ''', (nombre, correo, hashed_password))
            conn.commit()
            
            flash('¡Cuenta creada con éxito! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('El correo ingresado ya está registrado.', 'error')
        finally:
            conn.close()
            
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuarios WHERE correo = ?', (correo,)).fetchone()
        conn.close()
        
        # Verificamos que el usuario exista y que la contraseña coincida con el hash
        if usuario and bcrypt.check_password_hash(usuario['password_hash'], password):
            session['usuario_id'] = usuario['id_usuario']
            session['nombre'] = usuario['nombre']
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos. Inténtalo de nuevo.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Borra los datos de la sesión
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)