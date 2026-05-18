-- =====================================================
-- CALIGUÍA - ESQUEMA CORREGIDO (SIN FOREIGN KEYS CON ARRAYS)
-- =====================================================

-- =====================================================
-- 1. LUGARES TURÍSTICOS (ATRACTIVOS)
-- =====================================================
CREATE TABLE lugares (
    id SERIAL PRIMARY KEY,
    codigo_recurso VARCHAR(100) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    descripcion_corta VARCHAR(300),
    direccion TEXT,
    ciudad VARCHAR(50) DEFAULT 'Santiago de Cali',
    departamento VARCHAR(50) DEFAULT 'Valle del Cauca',
    corredor VARCHAR(100) DEFAULT 'Corredor Turístico del Pacífico',
    zona VARCHAR(50) CHECK (zona IN ('centro', 'sur', 'norte', 'este', 'oeste', 'pance')),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    
    -- Clasificación patrimonial
    tipo_patrimonio VARCHAR(50) CHECK (tipo_patrimonio IN ('Patrimonio Cultural', 'Patrimonio Natural')),
    subtipo_patrimonio VARCHAR(100),
    componente VARCHAR(100),
    
    -- Intereses para perfilamiento
    categorias TEXT[],
    etiquetas TEXT[],
    
    -- Horarios y precios
    horario VARCHAR(200),
    horario_detalle JSONB,
    precio VARCHAR(100),
    precio_aprox INTEGER,
    moneda VARCHAR(3) DEFAULT 'COP',
    
    -- Contacto digital
    pagina_web VARCHAR(200),
    facebook VARCHAR(200),
    instagram VARCHAR(200),
    twitter VARCHAR(200),
    tiktok VARCHAR(200),
    
    -- Multimedia
    imagen_principal TEXT,
    galeria_imagenes TEXT[],
    video_promo VARCHAR(200),
    audio_guia TEXT,
    
    -- Datos enriquecidos
    historia TEXT,
    tip_caleño TEXT,
    datos_curiosos TEXT[],
    
    -- Para reconocimiento visual (Computer Vision)
    features_vision JSONB,
    imagen_referencia TEXT[],
    
    -- Métricas
    rating_promedio DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    visitas_mensuales INTEGER DEFAULT 0,
    tiempo_recomendado_minutos INTEGER,
    
    -- Metadatos
    activo BOOLEAN DEFAULT true,
    destacado BOOLEAN DEFAULT false,
    orden_destacado INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 2. EVENTOS (Calendario Turístico)
-- =====================================================
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    codigo_recurso VARCHAR(100) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    descripcion_corta VARCHAR(300),
    
    -- Fechas
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    año INTEGER,
    mes_ejecucion INTEGER,
    es_anual BOOLEAN DEFAULT true,
    
    -- Ubicación
    ubicacion_nombre VARCHAR(200),
    lugar_id INTEGER REFERENCES lugares(id),
    direccion TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    
    -- Clasificación
    tipo_evento VARCHAR(50) CHECK (tipo_evento IN ('cultural', 'salsa', 'musica', 'deportivo', 'gastronomico', 'feria', 'religioso', 'literario', 'cine', 'teatro', 'naturaleza')),
    escala VARCHAR(30) CHECK (escala IN ('internacional', 'nacional', 'regional', 'local')),
    ancla BOOLEAN DEFAULT false,
    
    -- Capacidad y público
    aforo_estimado INTEGER,
    perfil_usuario TEXT[],
    
    -- Precios
    precio VARCHAR(100),
    precio_desde INTEGER,
    es_gratuito BOOLEAN DEFAULT false,
    
    -- Contenido
    actividades TEXT[],
    artistas_invitados TEXT[],
    paises_participantes TEXT[],
    
    -- Contacto
    pagina_web VARCHAR(200),
    facebook VARCHAR(200),
    instagram VARCHAR(200),
    
    -- Multimedia
    imagen_principal TEXT,
    imagen_promo TEXT,
    
    -- Estado
    destacado BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 3. GASTRONOMÍA (CORREGIDA - Sin array problemático)
-- =====================================================
CREATE TABLE gastronomia (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    ingredientes TEXT[],
    origen VARCHAR(100),
    
    -- Precios
    precio_promedio VARCHAR(50),
    precio_min INTEGER,
    precio_max INTEGER,
    
    -- Dónde encontrarlo
    lugares_destacados TEXT[],  -- Nombres de lugares, no IDs (para simplificar)
    
    -- Tipo de plato
    tipo_plato VARCHAR(50) CHECK (tipo_plato IN ('bebida', 'comida_tipica', 'postre', 'desayuno', 'comida_rapida')),
    es_tradicional BOOLEAN DEFAULT true,
    
    -- Multimedia
    imagen TEXT,
    video_receta VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 3b. TABLA PUENTE: GASTRONOMÍA → LUGARES (CORRECCIÓN)
-- =====================================================
CREATE TABLE gastronomia_lugares (
    id SERIAL PRIMARY KEY,
    gastronomia_id INTEGER REFERENCES gastronomia(id) ON DELETE CASCADE,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(gastronomia_id, lugar_id)
);

-- =====================================================
-- 4. RUTAS Y SENDEROS
-- =====================================================
CREATE TABLE rutas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- Características
    tipo_ruta VARCHAR(50) CHECK (tipo_ruta IN ('peatonal', 'caminata', 'bicicleta', 'mixto')),
    dificultad VARCHAR(20) CHECK (dificultad IN ('baja', 'media', 'alta')),
    distancia_km DECIMAL(6,2),
    duracion_estimada_minutos INTEGER,
    desnivel_mts INTEGER,
    
    -- Punto de inicio y fin
    punto_inicio_lat DOUBLE PRECISION,
    punto_inicio_lng DOUBLE PRECISION,
    punto_fin_lat DOUBLE PRECISION,
    punto_fin_lng DOUBLE PRECISION,
    
    -- Recomendaciones
    recomendaciones TEXT,
    restricciones TEXT,
    
    -- Multimedia
    imagen_ruta TEXT,
    mapa_ruta TEXT,
    gpx_track TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 4b. TABLA PUENTE: RUTAS → LUGARES
-- =====================================================
CREATE TABLE rutas_lugares (
    id SERIAL PRIMARY KEY,
    ruta_id INTEGER REFERENCES rutas(id) ON DELETE CASCADE,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    orden INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ruta_id, lugar_id)
);

-- =====================================================
-- 5. USUARIOS
-- =====================================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(100),
    avatar TEXT,
    
    -- Preferencias del usuario (para personalización)
    intereses TEXT[],
    estilo_viaje VARCHAR(30) CHECK (estilo_viaje IN ('aventura', 'relax', 'cultural', 'gastronomico', 'familiar', 'solo')),
    presupuesto VARCHAR(20) CHECK (presupuesto IN ('bajo', 'medio', 'alto')),
    idioma_preferido VARCHAR(10) DEFAULT 'es',
    
    -- Contexto de usuario
    ciudad_origen VARCHAR(100),
    edad INTEGER,
    
    -- Seguridad
    firebase_uid VARCHAR(200) UNIQUE,
    ultimo_acceso TIMESTAMP,
    
    -- Preferencias de notificación
    notificaciones_push BOOLEAN DEFAULT true,
    notificaciones_eventos BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 6. INTERACCIONES (Historial de usuario)
-- =====================================================
CREATE TABLE interacciones_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo VARCHAR(30) CHECK (tipo IN ('vista', 'click', 'like', 'favorito', 'visitado', 'compartido', 'audio_escuchado', 'qr_scanned')),
    lugar_id INTEGER REFERENCES lugares(id),
    evento_id INTEGER REFERENCES eventos(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- =====================================================
-- 7. LUGARES FAVORITOS
-- =====================================================
CREATE TABLE usuarios_lugares_favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id, lugar_id)
);

-- =====================================================
-- 8. EVENTOS FAVORITOS
-- =====================================================
CREATE TABLE usuarios_eventos_favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id, evento_id)
);

-- =====================================================
-- 9. RUTAS GUARDADAS POR USUARIO
-- =====================================================
CREATE TABLE rutas_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre_ruta VARCHAR(200),
    lugares_ids INTEGER[],
    orden_optimizado INTEGER[],
    distancia_km DECIMAL(6,2),
    duracion_estimada_minutos INTEGER,
    categoria VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 10. RESEÑAS Y VALORACIONES
-- =====================================================
CREATE TABLE resenas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    calificacion INTEGER CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    likes INTEGER DEFAULT 0,
    fecha TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 11. GEOCERCAS
-- =====================================================
CREATE TABLE geocercas (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    radio_metros INTEGER DEFAULT 100,
    lat_center DOUBLE PRECISION,
    lng_center DOUBLE PRECISION,
    mensaje_bienvenida TEXT,
    mensaje_evento TEXT,
    activo BOOLEAN DEFAULT true
);

-- =====================================================
-- 12. NOTIFICACIONES ENVIADAS
-- =====================================================
CREATE TABLE notificaciones_enviadas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    evento_id INTEGER REFERENCES eventos(id),
    lugar_id INTEGER REFERENCES lugares(id),
    titulo VARCHAR(200),
    mensaje TEXT,
    fecha_envio TIMESTAMP DEFAULT NOW(),
    entregada BOOLEAN DEFAULT true
);

-- =====================================================
-- 13. IMÁGENES DE REFERENCIA (para Computer Vision)
-- =====================================================
CREATE TABLE imagenes_referencia (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    imagen_url TEXT,
    angulo VARCHAR(20),
    condiciones_luz VARCHAR(30),
    vector_embedding JSONB,
    activo BOOLEAN DEFAULT true
);

-- =====================================================
-- 14. AUDIOS GUÍA (versiones por idioma/voz)
-- =====================================================
CREATE TABLE audios_guia (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER REFERENCES lugares(id) ON DELETE CASCADE,
    tipo_voz VARCHAR(30) DEFAULT 'caleña',
    idioma VARCHAR(10) DEFAULT 'es',
    audio_url TEXT,
    duracion_segundos INTEGER,
    transcripcion TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================
CREATE INDEX idx_lugares_lat_lng ON lugares(lat, lng);
CREATE INDEX idx_lugares_categorias ON lugares USING GIN(categorias);
CREATE INDEX idx_lugares_etiquetas ON lugares USING GIN(etiquetas);
CREATE INDEX idx_lugares_destacado ON lugares(destacado) WHERE destacado = true;

CREATE INDEX idx_eventos_fechas ON eventos(fecha_inicio, fecha_fin);
CREATE INDEX idx_eventos_ancla ON eventos(ancla) WHERE ancla = true;
CREATE INDEX idx_eventos_tipo ON eventos(tipo_evento);

CREATE INDEX idx_usuarios_intereses ON usuarios USING GIN(intereses);
CREATE INDEX idx_interacciones_usuario_tiempo ON interacciones_usuario(usuario_id, timestamp);
CREATE INDEX idx_resenas_lugar ON resenas(lugar_id);
CREATE INDEX idx_resenas_calificacion ON resenas(calificacion);

CREATE INDEX idx_geocercas_ubicacion ON geocercas(lat_center, lng_center) WHERE activo = true;
CREATE INDEX idx_imagenes_referencia_lugar ON imagenes_referencia(lugar_id);


-- =====================================================
-- INSERCIÓN DE DATOS CORREGIDA
-- =====================================================

-- Insertar lugares (sin cambios)
INSERT INTO lugares (nombre, lat, lng, categorias, etiquetas, descripcion_corta, tip_caleño) VALUES
('Iglesia La Ermita', 3.4548, -76.5328, ARRAY['cultura', 'historia'], ARRAY['iglesia', 'gotico'], 'Estilo gótico inspirado en la Catedral de Colonia.', '¡Oís, esta iglesia parece sacada de un cuento europeo!'),
('El Gato del Río', 3.4504, -76.5411, ARRAY['cultura', 'arte'], ARRAY['escultura', 'arte_publico'], 'Escultura de Hernando Tejada rodeada por "las gatas de la ribera".', '¡El gato más famoso de Cali! Asegurate de tomar foto con los 12 gatos.'),
('Cristo Rey', 3.4364, -76.5658, ARRAY['cultura', 'historia', 'religioso'], ARRAY['monumento', 'mirador'], 'Estatua de 26 metros en el Cerro de los Cristales.', 'Subí tempranito, el sol aquí pega duro pero la vista es una chimba.'),
('Barrio San Antonio', 3.4475, -76.5414, ARRAY['cultura', 'gastronomia', 'historia'], ARRAY['barrio', 'colonial', 'bohemio'], 'Calles empedradas y arquitectura colonial.', 'El plan es venir en la noche, te tomás una lulada y ves la ciudad desde arriba.'),
('Río Pance', 3.3325, -76.6322, ARRAY['naturaleza', 'ecoturismo'], ARRAY['rio', 'senderismo', 'avistamiento'], 'Destino tradicional de naturaleza y "baño de río".', 'Llevá bloqueador, repelente y muchas ganas de fresco.'),
('Plazoleta Jairo Varela', 3.4545, -76.5342, ARRAY['salsa', 'cultura'], ARRAY['salsa', 'musica', 'monumento'], 'Museo interactivo de la salsa y monumento "Cali Pachanguero".', 'Aquí se respira salsa, oís. El homenaje al creador del Grupo Niche.');

-- Insertar gastronomía (sin referencias a IDs de lugares)
INSERT INTO gastronomia (nombre, ingredientes, origen, precio_promedio, precio_min, precio_max, tipo_plato, lugares_destacados) VALUES
('Pandebono', ARRAY['Harina de yuca', 'Harina de maíz', 'Queso', 'Azúcar', 'Huevos'], 'Dagua, Valle', '$1.500 - $2.000', 1500, 2000, 'desayuno', ARRAY['Todas las panaderías', 'Barrio San Antonio']),
('Chuleta Valluna', ARRAY['Pierna de cerdo', 'Comino', 'Orégano', 'Harina de trigo', 'Huevo'], 'Valle del Cauca', '$22.000 - $30.000', 22000, 30000, 'comida_tipica', ARRAY['Restaurantes del Centro', 'Galería Alameda']),
('Lulada', ARRAY['Lulo', 'Limon', 'Azúcar', 'Hielo'], 'Valle del Cauca', '$5.000 - $8.000', 5000, 8000, 'bebida', ARRAY['Galería Alameda', 'Barrio San Antonio', 'Bulevar del Río']),
('Marranita', ARRAY['Plátano verde', 'Chicharrón', 'Sal'], 'Pacífico colombiano', '$3.000 - $5.000', 3000, 5000, 'comida_rapida', ARRAY['Galería Alameda', 'Ferias gastronómicas']),
('Cholado', ARRAY['Hielo raspado', 'Frutas variadas', 'Jarabe'], 'Jamundí, Valle', '$6.000 - $9.000', 6000, 9000, 'bebida', ARRAY['Unidad Deportiva Panamericana', 'Parque del Perro']),
('Champús', ARRAY['Maíz', 'Piña', 'Lulo', 'Panela', 'Canela'], 'Valle del Cauca', '$4.000 - $5.000', 4000, 5000, 'bebida', ARRAY['Barrio San Antonio', 'Galerías']);

-- Insertar relación gastronomía → lugares (tabla puente)
-- Primero obtenemos los IDs de lugares
DO $$
DECLARE
    v_san_antonio_id INTEGER;
    v_galeria_alameda_id INTEGER;
    v_bulevar_id INTEGER;
    v_unidad_deportiva_id INTEGER;
BEGIN
    SELECT id INTO v_san_antonio_id FROM lugares WHERE nombre = 'Barrio San Antonio' LIMIT 1;
    SELECT id INTO v_galeria_alameda_id FROM lugares WHERE nombre = 'Barrio San Antonio' LIMIT 1; -- Placeholder
    SELECT id INTO v_bulevar_id FROM lugares WHERE nombre = 'Plazoleta Jairo Varela' LIMIT 1; -- Placeholder
    SELECT id INTO v_unidad_deportiva_id FROM lugares WHERE nombre = 'Cristo Rey' LIMIT 1; -- Placeholder
    
    -- Lulada (id=3) se encuentra en Barrio San Antonio
    IF v_san_antonio_id IS NOT NULL THEN
        INSERT INTO gastronomia_lugares (gastronomia_id, lugar_id) VALUES (3, v_san_antonio_id);
    END IF;
END $$;

-- Insertar eventos calendario 2026
INSERT INTO eventos (nombre, fecha_inicio, fecha_fin, tipo_evento, escala, ancla, perfil_usuario) VALUES
('Colombia BirdFair', '2026-02-15', '2026-02-18', 'naturaleza', 'internacional', false, ARRAY['naturaleza']),
('Festival de Música Clásica', '2026-03-25', '2026-04-04', 'musica', 'internacional', false, ARRAY['cultura']),
('Festival Petronio Álvarez', '2026-08-14', '2026-08-19', 'musica', 'internacional', true, ARRAY['cultura', 'gastronomia', 'salsa']),
('Festival Mundial de Salsa', '2026-09-12', '2026-09-20', 'salsa', 'internacional', true, ARRAY['salsa']),
('Feria de Cali', '2026-12-25', '2026-12-30', 'cultural', 'internacional', true, ARRAY['salsa', 'cultura', 'gastronomia']),
('Festival de Macetas', '2026-06-24', '2026-06-29', 'cultural', 'nacional', false, ARRAY['cultura', 'familiar']),
('Sucursal Fest', '2026-07-17', '2026-07-19', 'cultural', 'nacional', false, ARRAY['cultura']);

-- Insertar rutas
INSERT INTO rutas (nombre, tipo_ruta, dificultad, distancia_km, duracion_estimada_minutos) VALUES
('Ruta Centro Histórico', 'peatonal', 'baja', 3.5, 120),
('Ruta de la Salsa', 'peatonal', 'baja', 2.8, 90),
('Ruta de los Cerros', 'caminata', 'alta', 8.5, 240);

-- Insertar relación rutas → lugares
INSERT INTO rutas_lugares (ruta_id, lugar_id, orden) VALUES
(1, 1, 1),  -- Ruta Centro Histórico → Iglesia La Ermita (orden 1)
(1, 4, 2),  -- Ruta Centro Histórico → Barrio San Antonio (orden 2)
(1, 3, 3),  -- Ruta Centro Histórico → Cristo Rey (orden 3)
(2, 6, 1),  -- Ruta de la Salsa → Plazoleta Jairo Varela (orden 1)
(2, 4, 2),  -- Ruta de la Salsa → Barrio San Antonio (orden 2)
(3, 3, 1);  -- Ruta de los Cerros → Cristo Rey (orden 1)