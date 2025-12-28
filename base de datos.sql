-- =============================================
-- TABLAS MAESTRAS Y CONFIGURACIÓN
-- =============================================

-- Marcas de productos
CREATE TABLE marcas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Distribuidores/Proveedores
CREATE TABLE distribuidores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    nit VARCHAR(20) UNIQUE,
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    tarjeta_credito VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Empleados/Personal
CREATE TABLE empleados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    puesto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    usuario VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    ultimo_ingreso TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    fecha_contratacion DATE DEFAULT CURRENT_DATE
);

-- =============================================
-- TABLA PRINCIPAL DE PRODUCTOS CON RFID
-- =============================================

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    epc VARCHAR(24) UNIQUE NOT NULL,           -- EPC RFID de 96 bits
    codigo_barras VARCHAR(50) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    marca_id INTEGER REFERENCES marcas(id),
    distribuidor_id INTEGER REFERENCES distribuidores(id),
    fecha_vencimiento DATE,
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    peso DECIMAL(10,2),
    precio_compra DECIMAL(10,2),
    precio_venta DECIMAL(10,2),
    stock INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 0,
    ubicacion VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

-- =============================================
-- TABLAS DE TRANSACCIONES
-- =============================================

-- Compras a proveedores
CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    distribuidor_id INTEGER REFERENCES distribuidores(id),
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) DEFAULT 0,
    iva DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    descripcion TEXT,
    empleado_id INTEGER REFERENCES empleados(id),
    estado VARCHAR(20) DEFAULT 'COMPLETADA'
);

-- Detalle de Compras
CREATE TABLE compra_detalle (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER REFERENCES compras(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- Ventas a clientes
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INTEGER REFERENCES clientes(id),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) DEFAULT 0,
    iva DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    descripcion TEXT,
    numero_caja VARCHAR(20),
    empleado_id INTEGER REFERENCES empleados(id),
    estado VARCHAR(20) DEFAULT 'COMPLETADA'
);

-- Detalle de Ventas
CREATE TABLE venta_detalle (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER REFERENCES ventas(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- =============================================
-- TABLA DE LECTURAS RFID (CRÍTICA PARA TU SISTEMA)
-- =============================================

CREATE TABLE lecturas_rfid (
    id SERIAL PRIMARY KEY,
    epc VARCHAR(24) NOT NULL,                   -- EPC leído del tag
    producto_id INTEGER REFERENCES productos(id),
    ubicacion VARCHAR(100) NOT NULL,            -- Donde se leyó (Almacén, Entrada, Salida)
    tipo_lectura VARCHAR(50) NOT NULL,          -- INGRESO, SALIDA, INVENTARIO, CONTEO
    fecha_lectura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lecturador_id INTEGER,                      -- ID del lector RFID o empleado
    compra_id INTEGER REFERENCES compras(id),   -- Relación con compra (si aplica)
    venta_id INTEGER REFERENCES ventas(id)      -- Relación con venta (si aplica)
);

-- =============================================
-- ÍNDICES PARA OPTIMIZAR CONSULTAS RFID
-- =============================================

CREATE INDEX idx_productos_epc ON productos(epc);
CREATE INDEX idx_lecturas_rfid_epc ON lecturas_rfid(epc);
CREATE INDEX idx_lecturas_rfid_fecha ON lecturas_rfid(fecha_lectura);
CREATE INDEX idx_lecturas_rfid_ubicacion ON lecturas_rfid(ubicacion);
CREATE INDEX idx_lecturas_rfid_tipo ON lecturas_rfid(tipo_lectura);
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);
CREATE INDEX idx_compras_fecha ON compras(fecha_compra);