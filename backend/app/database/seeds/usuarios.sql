-- =====================================================
-- SEED: Usuarios y preferencias
-- =====================================================

-- Nota: Los usuarios se crean normalmente a través de Supabase Auth
-- Este seed es para datos de demostración con usuarios existentes

-- Limpiar datos existentes
-- TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE;
-- TRUNCATE TABLE usuario_intereses CASCADE;
-- TRUNCATE TABLE favoritos CASCADE;
-- TRUNCATE TABLE resenas CASCADE;

-- Insertar usuarios de ejemplo
INSERT INTO usuarios (id, email, nombre, ciudad, edad, avatar, created_at) VALUES
(1, 'juan.perez@email.com', 'Juan Pérez', 'Cali', 28, 'https://randomuser.me/api/portraits/men/1.jpg', NOW()),
(2, 'maria.garcia@email.com', 'María García', 'Bogotá', 32, 'https://randomuser.me/api/portraits/women/2.jpg', NOW()),
(3, 'carlos.lopez@email.com', 'Carlos López', 'Medellín', 25, 'https://randomuser.me/api/portraits/men/3.jpg', NOW()),
(4, 'laura.martinez@email.com', 'Laura Martínez', 'Cali', 29, 'https://randomuser.me/api/portraits/women/4.jpg', NOW()),
(5, 'pedro.sanchez@email.com', 'Pedro Sánchez', 'Miami', 35, 'https://randomuser.me/api/portraits/men/5.jpg', NOW());

-- Insertar intereses de usuarios
INSERT INTO usuario_intereses (usuario_id, interes) VALUES
(1, 'cultura'), (1, 'gastronomia'),
(2, 'naturaleza'), (2, 'cultura'),
(3, 'gastronomia'),
(4, 'cultura'), (4, 'naturaleza'), (4, 'gastronomia'),
(5, 'salsa'), (5, 'aventura');

-- Insertar favoritos
INSERT INTO favoritos (usuario_id, lugar_id, fecha_agregado) VALUES
(1, 1, NOW()), (1, 5, NOW()), (1, 9, NOW()),
(2, 4, NOW()), (2, 6, NOW()),
(3, 5, NOW()), (3, 10, NOW()),
(4, 1, NOW()), (4, 2, NOW()), (4, 3, NOW()), (4, 6, NOW()), (4, 8, NOW()),
(5, 8, NOW()), (5, 9, NOW());

-- Insertar reseñas de usuarios
INSERT INTO resenas (usuario_id, lugar_id, rating, comentario, fecha) VALUES
(1, 1, 5, 'Vista increíble, totalmente recomendado. El mejor mirador de Cali.', NOW()),
(1, 2, 4, 'Interesante obra de arte, representa la cultura caleña.', NOW()),
(2, 4, 5, 'Naturaleza pura, el mejor lugar para desconectarse.', NOW()),
(2, 6, 5, 'Excelente zoológico, muy bien cuidado.', NOW()),
(3, 5, 5, 'Excelente vida nocturna, muchas opciones para comer.', NOW()),
(3, 10, 5, 'Comida espectacular, el mejor restaurante de Cali.', NOW()),
(4, 1, 5, 'El mejor mirador de Cali, vista 360° imperdible.', NOW()),
(4, 3, 4, 'Arquitectura hermosa, iglesia muy bien conservada.', NOW()),
(4, 8, 5, 'Excelente lugar para aprender salsa, ambiente auténtico.', NOW()),
(5, 9, 5, 'La mejor salsa de Cali, ambiente único.', NOW()),
(5, 8, 4, 'Excelente ambiente, música en vivo de calidad.', NOW());

-- Insertar rutas de ejemplo
INSERT INTO rutas_usuario (id, usuario_id, nombre, descripcion, fecha_creacion) VALUES
(1, 1, 'Tour Cultural por Cali', 'Recorrido por los principales sitios culturales de la ciudad', NOW()),
(2, 2, 'Naturaleza y Aventura', 'Descubre los espacios naturales más impresionantes de Cali', NOW()),
(3, 4, 'Gastronomía Caleña', 'Los mejores lugares para comer en Cali', NOW()),
(4, 5, 'Ruta Salsera', 'Vive la mejor salsa caleña', NOW());

-- Insertar detalles de rutas
INSERT INTO ruta_detalle (ruta_id, lugar_id, orden, hora_estimada) VALUES
-- Ruta 1: Tour Cultural
(1, 3, 1, '09:00:00'),  -- Iglesia La Ermita
(1, 2, 2, '11:00:00'),  -- El Gato del Río
(1, 7, 3, '15:00:00'),  -- San Antonio
(1, 1, 4, '17:00:00'),  -- Cristo Rey
-- Ruta 2: Naturaleza
(2, 4, 1, '08:00:00'),  -- Río Pance
(2, 6, 2, '13:00:00'),  -- Zoológico
-- Ruta 3: Gastronomía
(3, 5, 1, '19:00:00'),  -- Bulevar del Río
(3, 10, 2, '21:00:00'), -- Morada Ancestral
-- Ruta 4: Salsa
(4, 8, 1, '20:00:00'),  -- Plazoleta Jairo Varela
(4, 9, 2, '22:00:00');  -- La Topa Tolondra

-- Reiniciar secuencias
SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios));
SELECT setval('rutas_usuario_id_seq', (SELECT MAX(id) FROM rutas_usuario));
SELECT setval('ruta_detalle_id_seq', (SELECT MAX(id) FROM ruta_detalle));