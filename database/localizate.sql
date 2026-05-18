# Guardar el esquema SQL de Supabase
sql_schema = '''
-- =====================================================
-- SUPABASE SCHEMA: localizate_db
-- Guía turística inteligente de Cali
-- =====================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- Para coordenadas geográficas

-- =====================================================
-- TABLAS PRINCIPALES
-- =====================================================

-- 1. CATEGORÍAS DE INTERÉS
CREATE TABLE categorias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(50) UNIQUE NOT NULL,  -- cultura, naturaleza, gastronomia, salsa, aventura
    nombre VARCHAR(100) NOT NULL,
    icono VARCHAR(10) DEFAULT '📍',
    color VARCHAR(7) DEFAULT '#FF6B35',
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. LUGARES TURÍSTICOS
CREATE TABLE lugares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE,
    descripcion TEXT NOT NULL,
    descripcion_corta VARCHAR(300),
    
    -- Ubicación (PostGIS para queries geoespaciales)
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    ubicacion GEOGRAPHY(POINT, 4326),  -- PostGIS point
    
    direccion VARCHAR(300),
    barrio VARCHAR(100),
    comuna VARCHAR(50),
    
    -- Categorización
    categoria_id UUID REFERENCES categorias(id) ON DELETE SET NULL,
    subcategorias TEXT[],  -- ['museo', 'patrimonio', 'arquitectura']
    
    -- Detalles
    icono VARCHAR(10) DEFAULT '📍',
    horario VARCHAR(200),
    precio VARCHAR(100),  -- "Gratis", "$25.000 COP", "Desde $15.000 COP"
    precio_min INTEGER,   -- en pesos COP para filtros
    precio_max INTEGER,
    
    -- Métricas
    rating DECIMAL(2, 1) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    
    -- Media
    imagen_principal VARCHAR(500),
    imagenes TEXT[],  -- URLs de galería
    video_url VARCHAR(500),
    
    -- Estado
    destacado BOOLEAN DEFAULT FALSE,
    verificado BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Metadatos
    telefono VARCHAR(50),
    sitio_web VARCHAR(300),
    instagram VARCHAR(100),
    email VARCHAR(200),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. EVENTOS
CREATE TABLE eventos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE,
    descripcion TEXT NOT NULL,
    
    -- Fechas
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    hora_inicio TIME,
    hora_fin TIME,
    
    -- Periodicidad
    es_recurrente BOOLEAN DEFAULT FALSE,
    frecuencia VARCHAR(50),  -- 'semanal', 'mensual', 'anual'
    dias_semana INTEGER[],   -- [1,3,5] para lunes, miércoles, viernes
    
    -- Ubicación
    lugar_id UUID REFERENCES lugares(id) ON DELETE SET NULL,
    direccion VARCHAR(300),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    ubicacion GEOGRAPHY(POINT, 4326),
    
    -- Detalles
    icono VARCHAR(10) DEFAULT '🎉',
    precio VARCHAR(100),
    precio_min INTEGER,
    capacidad INTEGER,
    
    -- Categorización
    tags TEXT[],
    categoria_id UUID REFERENCES categorias(id),
    
    -- Media
    imagen_principal VARCHAR(500),
    imagenes TEXT[],
    
    -- Estado
    destacado BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. USUARIOS (integrado con Supabase Auth)
CREATE TABLE perfiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    avatar_url VARCHAR(500),
    telefono VARCHAR(50),
    ciudad_origen VARCHAR(100),
    pais VARCHAR(100),
    
    -- Preferencias
    intereses UUID[] REFERENCES categorias(id),  -- IDs de categorías favoritas
    notificaciones_email BOOLEAN DEFAULT TRUE,
    notificaciones_push BOOLEAN DEFAULT TRUE,
    idioma VARCHAR(10) DEFAULT 'es',
    tema VARCHAR(10) DEFAULT 'light',
    
    -- Ubicación actual
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    ubicacion_actual GEOGRAPHY(POINT, 4326),
    
    -- Métricas
    total_rutas INTEGER DEFAULT 0,
    total_favoritos INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. RUTAS (itinerarios guardados)
CREATE TABLE rutas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id) ON DELETE CASCADE,
    
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- Configuración
    fecha_visita DATE,
    hora_inicio TIME,
    
    -- Métricas calculadas
    distancia_total_km DECIMAL(8, 2) DEFAULT 0,
    tiempo_estimado_min INTEGER DEFAULT 0,
    
    -- Estado
    completada BOOLEAN DEFAULT FALSE,
    compartida BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. DETALLE DE RUTA (lugares en orden)
CREATE TABLE ruta_detalles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ruta_id UUID REFERENCES rutas(id) ON DELETE CASCADE,
    lugar_id UUID REFERENCES lugares(id) ON DELETE CASCADE,
    
    orden INTEGER NOT NULL,
    
    -- Distancia desde el punto anterior
    distancia_desde_anterior_km DECIMAL(8, 2),
    tiempo_estimado_min INTEGER,
    
    -- Notas del usuario
    notas TEXT,
    hora_llegada_estimada TIME,
    
    visitado BOOLEAN DEFAULT FALSE,
    
    UNIQUE(ruta_id, orden)
);

-- 7. FAVORITOS
CREATE TABLE favoritos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id) ON DELETE CASCADE,
    lugar_id UUID REFERENCES lugares(id) ON DELETE CASCADE,
    
    notas TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(usuario_id, lugar_id)
);

-- 8. RESEÑAS
CREATE TABLE resenas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id) ON DELETE CASCADE,
    lugar_id UUID REFERENCES lugares(id) ON DELETE CASCADE,
    
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comentario TEXT,
    
    -- Media
    fotos TEXT[],
    
    -- Estado
    verificada BOOLEAN DEFAULT FALSE,  -- visita verificada por GPS
    activa BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. CHAT / CONVERSACIONES
CREATE TABLE conversaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id) ON DELETE CASCADE,
    
    titulo VARCHAR(200),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE mensajes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversacion_id UUID REFERENCES conversaciones(id) ON DELETE CASCADE,
    
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('user', 'assistant', 'system')),
    contenido TEXT NOT NULL,
    
    -- Metadatos del mensaje
    intencion VARCHAR(50),  -- 'salsa', 'gastronomia', 'ruta', etc.
    lugares_referenciados UUID[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. LOGS DE ACTIVIDAD (analytics)
CREATE TABLE actividad_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id) ON DELETE SET NULL,
    
    tipo VARCHAR(50) NOT NULL,  -- 'view_lugar', 'add_favorito', 'plan_ruta', 'chat_message'
    entidad_tipo VARCHAR(50),   -- 'lugar', 'evento', 'ruta'
    entidad_id UUID,
    
    -- Datos de contexto
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    dispositivo VARCHAR(50),
    navegador VARCHAR(100),
    
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES
-- =====================================================

-- Geoespaciales
CREATE INDEX idx_lugares_ubicacion ON lugares USING GIST(ubicacion);
CREATE INDEX idx_eventos_ubicacion ON eventos USING GIST(ubicacion);
CREATE INDEX idx_perfiles_ubicacion ON perfiles USING GIST(ubicacion_actual);

-- Búsquedas comunes
CREATE INDEX idx_lugares_categoria ON lugares(categoria_id) WHERE activo = TRUE;
CREATE INDEX idx_lugares_rating ON lugares(rating DESC) WHERE activo = TRUE;
CREATE INDEX idx_lugares_destacado ON lugares(destacado) WHERE destacado = TRUE;
CREATE INDEX idx_eventos_fechas ON eventos(fecha_inicio, fecha_fin) WHERE activo = TRUE;
CREATE INDEX idx_rutas_usuario ON rutas(usuario_id, created_at DESC);
CREATE INDEX idx_mensajes_conversacion ON mensajes(conversacion_id, created_at);
CREATE INDEX idx_actividad_usuario ON actividad_logs(usuario_id, created_at DESC);

-- Búsqueda de texto
CREATE INDEX idx_lugares_busqueda ON lugares USING gin(to_tsvector('spanish', nombre || ' ' || COALESCE(descripcion, '')));
CREATE INDEX idx_eventos_busqueda ON eventos USING gin(to_tsvector('spanish', nombre || ' ' || COALESCE(descripcion, '')));

-- =====================================================
-- FUNCIONES Y TRIGGERS
-- =====================================================

-- Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_lugares_updated_at BEFORE UPDATE ON lugares
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_eventos_updated_at BEFORE UPDATE ON eventos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_perfiles_updated_at BEFORE UPDATE ON perfiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_rutas_updated_at BEFORE UPDATE ON rutas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_resenas_updated_at BEFORE UPDATE ON resenas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Actualizar rating promedio de lugar cuando se agrega/edita reseña
CREATE OR REPLACE FUNCTION actualizar_rating_lugar()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE lugares
    SET rating = (
        SELECT ROUND(AVG(rating)::numeric, 1)
        FROM resenas
        WHERE lugar_id = COALESCE(NEW.lugar_id, OLD.lugar_id) AND activa = TRUE
    ),
    total_reviews = (
        SELECT COUNT(*)
        FROM resenas
        WHERE lugar_id = COALESCE(NEW.lugar_id, OLD.lugar_id) AND activa = TRUE
    )
    WHERE id = COALESCE(NEW.lugar_id, OLD.lugar_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_actualizar_rating
    AFTER INSERT OR UPDATE OR DELETE ON resenas
    FOR EACH ROW EXECUTE FUNCTION actualizar_rating_lugar();

-- Calcular distancia total de ruta
CREATE OR REPLACE FUNCTION calcular_distancia_ruta(ruta_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    total_dist DECIMAL := 0;
    rec RECORD;
    prev_lat DECIMAL;
    prev_lng DECIMAL;
BEGIN
    -- Punto de inicio: ubicación del usuario
    SELECT p.latitud, p.longitud INTO prev_lat, prev_lng
    FROM rutas r
    JOIN perfiles p ON r.usuario_id = p.id
    WHERE r.id = ruta_uuid;
    
    FOR rec IN 
        SELECT l.latitud, l.longitud
        FROM ruta_detalles rd
        JOIN lugares l ON rd.lugar_id = l.id
        WHERE rd.ruta_id = ruta_uuid
        ORDER BY rd.orden
    LOOP
        total_dist := total_dist + (
            SELECT ST_Distance(
                ST_MakePoint(prev_lng, prev_lat)::geography,
                ST_MakePoint(rec.longitud, rec.latitud)::geography
            ) / 1000
        );
        prev_lat := rec.latitud;
        prev_lng := rec.longitud;
    END LOOP;
    
    RETURN ROUND(total_dist, 2);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- POLÍTICAS RLS (Row Level Security)
-- =====================================================

ALTER TABLE perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE rutas ENABLE ROW LEVEL SECURITY;
ALTER TABLE ruta_detalles ENABLE ROW LEVEL SECURITY;
ALTER TABLE favoritos ENABLE ROW LEVEL SECURITY;
ALTER TABLE resenas ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE mensajes ENABLE ROW LEVEL SECURITY;
ALTER TABLE actividad_logs ENABLE ROW LEVEL SECURITY;

-- Perfiles: solo el propio usuario puede ver/editar
CREATE POLICY "Usuarios ven su propio perfil" ON perfiles
    FOR ALL USING (auth.uid() = id);

-- Rutas: solo el dueño
CREATE POLICY "Usuarios gestionan sus rutas" ON rutas
    FOR ALL USING (auth.uid() = usuario_id);

-- Ruta detalles: a través de la ruta padre
CREATE POLICY "Usuarios gestionan detalles de sus rutas" ON ruta_detalles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM rutas r 
            WHERE r.id = ruta_detalles.ruta_id 
            AND r.usuario_id = auth.uid()
        )
    );

-- Favoritos: solo el dueño
CREATE POLICY "Usuarios gestionan sus favoritos" ON favoritos
    FOR ALL USING (auth.uid() = usuario_id);

-- Reseñas: visibles para todos, editables solo por el autor
CREATE POLICY "Reseñas visibles públicamente" ON resenas
    FOR SELECT USING (activa = TRUE);
    
CREATE POLICY "Usuarios gestionan sus reseñas" ON resenas
    FOR ALL USING (auth.uid() = usuario_id);

-- Conversaciones y mensajes: solo el dueño
CREATE POLICY "Usuarios gestionan sus conversaciones" ON conversaciones
    FOR ALL USING (auth.uid() = usuario_id);
    
CREATE POLICY "Usuarios gestionan sus mensajes" ON mensajes
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM conversaciones c 
            WHERE c.id = mensajes.conversacion_id 
            AND c.usuario_id = auth.uid()
        )
    );

-- Logs: solo el dueño
CREATE POLICY "Usuarios ven sus logs" ON actividad_logs
    FOR SELECT USING (auth.uid() = usuario_id);

-- Lugares y eventos: públicos (solo lectura)
CREATE POLICY "Lugares públicos" ON lugares FOR SELECT USING (activo = TRUE);
CREATE POLICY "Eventos públicos" ON eventos FOR SELECT USING (activo = TRUE);
CREATE POLICY "Categorías públicas" ON categorias FOR SELECT USING (activo = TRUE);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

INSERT INTO categorias (slug, nombre, icono, color, descripcion, orden) VALUES
('cultura', 'Cultura', '🎭', '#FF6B35', 'Museos, iglesias, arte y patrimonio', 1),
('naturaleza', 'Naturaleza', '🌳', '#2ECC71', 'Parques, ríos, montañas y fauna', 2),
('gastronomia', 'Gastronomía', '🍽️', '#E74C3C', 'Restaurantes, mercados y experiencias culinarias', 3),
('salsa', 'Salsa', '💃', '#9B59B6', 'Bares, clubes y eventos de salsa', 4),
('aventura', 'Aventura', '🧗', '#3498DB', 'Deportes extremos y actividades al aire libre', 5);

-- Insertar lugares de ejemplo (solo algunos, el resto vía API)
INSERT INTO lugares (nombre, slug, descripcion, descripcion_corta, latitud, longitud, ubicacion, direccion, barrio, categoria_id, icono, horario, precio, precio_min, precio_max, rating, destacado, verificado) VALUES
('Cristo Rey', 'cristo-rey', 'Estatua monumental de 26m con vista panorámica de toda la ciudad. Ideal para fotos al atardecer.', 'Estatua monumental con vista panorámica', 3.43587, -76.56490, ST_MakePoint(-76.56490, 3.43587)::geography, 'Cerro de los Cristales, Siloe', 'Siloe', (SELECT id FROM categorias WHERE slug = 'cultura'), '✝️', '8:00 AM - 6:00 PM', 'Gratis', 0, 0, 4.7, TRUE, TRUE),
('El Gato del Río', 'el-gato-del-rio', 'Escultura icónica de Hernando Tejada. Símbolo de la ciudad y punto de encuentro cultural.', 'Escultura icónica de la ciudad', 3.45156, -76.54297, ST_MakePoint(-76.54297, 3.45156)::geography, 'Avenida del Río con Carrera 1', 'Centro', (SELECT id FROM categorias WHERE slug = 'cultura'), '🐱', '24 horas', 'Gratis', 0, 0, 4.5, TRUE, TRUE),
('Iglesia La Ermita', 'iglesia-la-ermita', 'Templo neogótico del siglo XIX con vitrales impresionantes. Patrimonio arquitectónico.', 'Templo neogótico del siglo XIX', 3.4520, -76.53201, ST_MakePoint(-76.53201, 3.4520)::geography, 'Carrera 4 con Calle 13', 'Centro', (SELECT id FROM categorias WHERE slug = 'cultura'), '⛪', '6:00 AM - 8:00 PM', 'Gratis', 0, 0, 4.8, TRUE, TRUE),
('Río Pance', 'rio-pance', 'Pulmón natural de Cali. Charcos cristalinos, senderos ecológicos y avistamiento de aves.', 'Pulmón natural de Cali', 3.3325, -76.6322, ST_MakePoint(-76.6322, 3.3325)::geography, 'Vía a Pance, km 7', 'Pance', (SELECT id FROM categorias WHERE slug = 'naturaleza'), '🏞️', '7:00 AM - 5:00 PM', '$5.000 COP', 5000, 5000, 4.6, TRUE, TRUE),
('Zoológico de Cali', 'zoologico-de-cali', 'Uno de los mejores zoológicos de Latinoamérica. Más de 250 especies en hábitats naturales.', 'Uno de los mejores zoológicos de Latinoamérica', 3.4480, -76.5580, ST_MakePoint(-76.5580, 3.4480)::geography, 'Carrera 2 Oeste # 14-115', 'San Antonio', (SELECT id FROM categorias WHERE slug = 'naturaleza'), '🦁', '9:00 AM - 5:00 PM', '$25.000 COP', 25000, 25000, 4.8, TRUE, TRUE),
('La Topa Tolondra', 'la-topa-tolondra', 'Bar icónico de salsa caleña. Clases de baile, orquestas en vivo y ambiente inigualable.', 'Bar icónico de salsa caleña', 3.4540, -76.5310, ST_MakePoint(-76.5310, 3.4540)::geography, 'Calle 5 # 13-27', 'Centro', (SELECT id FROM categorias WHERE slug = 'salsa'), '🎵', '8:00 PM - 3:00 AM', 'Desde $20.000 COP', 20000, 50000, 4.8, TRUE, TRUE),
('Morada Ancestral', 'morada-ancestral', 'Restaurante top de Cali. Cocina del Pacífico con toque contemporáneo.', 'Cocina del Pacífico contemporánea', 3.4200, -76.5400, ST_MakePoint(-76.5400, 3.4200)::geography, 'Calle 9 # 48-81, Ciudad Jardín', 'Ciudad Jardín', (SELECT id FROM categorias WHERE slug = 'gastronomia'), '🍽️', '12:00 PM - 10:00 PM', '$80.000 - $150.000 COP', 80000, 150000, 4.9, TRUE, TRUE);

-- Insertar eventos de ejemplo
INSERT INTO eventos (nombre, slug, descripcion, fecha_inicio, fecha_fin, icono, precio, tags, categoria_id, destacado) VALUES
('Festival Mundial de Salsa 2026', 'festival-mundial-salsa-2026', 'El evento de salsa más grande del mundo. Competencias, conciertos y clases magistrales.', '2026-09-24', '2026-09-28', '🎺', 'Desde $50.000 COP', ARRAY['Salsa', 'Música', 'Competencia'], (SELECT id FROM categorias WHERE slug = 'salsa'), TRUE),
('Feria de Cali 2026', 'feria-de-cali-2026', 'La feria más importante de Colombia. Salsódromo, cabalgata, conciertos y cultura caleña.', '2026-12-25', '2026-12-30', '🎉', 'Varía', ARRAY['Cultura', 'Fiesta', 'Tradición'], (SELECT id FROM categorias WHERE slug = 'cultura'), TRUE),
('Festival Petronio Álvarez', 'festival-petronio-alvarez', 'Celebración de la música del Pacífico. Currulao, marimba y gastronomía afrocolombiana.', '2026-08-14', '2026-08-19', '🪘', 'Gratis', ARRAY['Cultura', 'Pacífico', 'Música'], (SELECT id FROM categorias WHERE slug = 'cultura'), TRUE);

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

CREATE VIEW lugares_con_categoria AS
SELECT 
    l.*,
    c.nombre as categoria_nombre,
    c.slug as categoria_slug,
    c.color as categoria_color,
    c.icono as categoria_icono
FROM lugares l
LEFT JOIN categorias c ON l.categoria_id = c.id
WHERE l.activo = TRUE;

CREATE VIEW eventos_proximos AS
SELECT 
    e.*,
    c.nombre as categoria_nombre,
    c.slug as categoria_slug,
    l.nombre as lugar_nombre
FROM eventos e
LEFT JOIN categorias c ON e.categoria_id = c.id
LEFT JOIN lugares l ON e.lugar_id = l.id
WHERE e.activo = TRUE 
AND e.fecha_fin >= CURRENT_DATE
ORDER BY e.fecha_inicio;

CREATE VIEW rutas_completas AS
SELECT 
    r.*,
    json_agg(
        json_build_object(
            'orden', rd.orden,
            'lugar', json_build_object(
                'id', l.id,
                'nombre', l.nombre,
                'latitud', l.latitud,
                'longitud', l.longitud,
                'icono', l.icono,
                'direccion', l.direccion
            ),
            'distancia_desde_anterior_km', rd.distancia_desde_anterior_km,
            'tiempo_estimado_min', rd.tiempo_estimado_min,
            'visitado', rd.visitado
        ) ORDER BY rd.orden
    ) as detalles
FROM rutas r
LEFT JOIN ruta_detalles rd ON r.id = rd.ruta_id
LEFT JOIN lugares l ON rd.lugar_id = l.id
WHERE r.activa = TRUE
GROUP BY r.id;
'''

with open('/mnt/agents/output/supabase_schema.sql', 'w', encoding='utf-8') as f:
    f.write(sql_schema)

print("✅ Esquema SQL guardado: supabase_schema.sql")