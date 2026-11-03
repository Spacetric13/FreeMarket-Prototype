import sqlite3

def crear_base_datos():
    # Conecta a la base de datos (si no existe, la crea como un archivo en tu carpeta)
    conexion = sqlite3.connect('marketplace.db')
    cursor = conexion.cursor()

    # Ejecuta la estructura SQL que diseñamos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) NOT NULL,
        correo VARCHAR(150) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        confirmado BOOLEAN DEFAULT 0,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos 'marketplace.db' y tabla 'usuarios' creadas con éxito.")

if __name__ == '__main__':
    crear_base_datos()