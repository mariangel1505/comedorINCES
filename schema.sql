-- SQL de inicialización para SGSC INCES
-- Ejecutar en la base de datos configurada en `conexion.py`.
-- Si no existe, crea la base de datos con:
--   CREATE DATABASE sistema_comedor;
-- Luego ejecuta:
--   psql -U postgres -p 5433 -d sistema_comedor -f schema.sql

CREATE TABLE IF NOT EXISTS usuarios (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    correo VARCHAR(150),
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consumos (
    id SERIAL PRIMARY KEY,
    cedula_usuario VARCHAR(20) NOT NULL,
    id_turno VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    creado_en TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (cedula_usuario) REFERENCES usuarios (cedula)
);

CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    evento VARCHAR(255) NOT NULL,
    origen VARCHAR(100),
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Datos de ejemplo para prueba
INSERT INTO usuarios (cedula, nombre, apellido, correo, ciudad, estado, codigo_postal) VALUES
('12345678', 'Ana', 'Pérez', 'ana.perez@inces.example', 'Caracas', 'Distrito Capital', '1010'),
('87654321', 'Juan', 'Ramirez', 'juan.ramirez@inces.example', 'Valencia', 'Carabobo', '2001')
ON CONFLICT (cedula) DO NOTHING;

INSERT INTO auditoria (evento, origen) VALUES
('Inicio de sesión de usuario', 'sistema'),
('Registro de consumo manual', 'dashboard');

INSERT INTO consumos (cedula_usuario, id_turno, fecha, hora) VALUES
('12345678', '1', CURRENT_DATE, '08:30'),
('87654321', '2', CURRENT_DATE, '12:15'),
('12345678', '1', CURRENT_DATE - INTERVAL '1 day', '07:50');
