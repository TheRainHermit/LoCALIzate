-- =====================================================
-- SEED: Eventos de Cali
-- =====================================================

-- Limpiar datos existentes
-- TRUNCATE TABLE eventos RESTART IDENTITY CASCADE;

INSERT INTO eventos (id, nombre, fecha_inicio, fecha_fin, descripcion, ubicacion, destacado, precio, horario, actividades, imagen) VALUES
(1, 'Feria de Cali 2026', '2026-12-25', '2026-12-30', 'La feria más importante de Colombia. Salsódromo, cabalgata, conciertos y cultura caleña.', 'Toda la ciudad', true, 'Eventos gratuitos y pagos', '8:00 AM - 2:00 AM', ARRAY['Salsódromo', 'Cabalgata', 'Conciertos masivos', 'Desfile de carrozas', 'Feria taurina', 'Calle de la Feria'], 'https://images.unsplash.com/photo-1597176394696-79e3223fed37'),

(2, 'Festival Mundial de Salsa 2026', '2026-09-12', '2026-09-20', 'Competencia mundial de baile de salsa. Los mejores bailarines del mundo.', 'Coliseo El Pueblo', true, 'Desde $50.000', '6:00 PM - 2:00 AM', ARRAY['Competencia de baile', 'Clases magistrales', 'Conciertos de orquestas', 'Ruedas de casino', 'Encuentros académicos'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9'),

(3, 'Festival Petronio Álvarez', '2026-08-14', '2026-08-19', 'Celebración de la música del Pacífico. Currulao, marimba y gastronomía afrocolombiana.', 'Unidad Deportiva', true, 'Gratis', '10:00 AM - 12:00 AM', ARRAY['Conciertos', 'Danzas tradicionales', 'Muestra gastronómica', 'Desfile de comparsas', 'Talleres de marimba'], 'https://images.unsplash.com/photo-1597176394696-79e3223fed37'),

(4, 'Salsa al Parque', '2026-12-10', '2026-12-15', 'Festival gratuito de salsa en espacios públicos. Orquestas y baile callejero.', 'Parque del Perro', true, 'Gratis', '4:00 PM - 10:00 PM', ARRAY['Conciertos al aire libre', 'Clases de baile', 'Competencias callejeras', 'DJ sets'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9'),

(5, 'Cali Visual Fest', '2026-05-15', '2026-05-25', 'Festival de arte urbano y visual. Galerías, murales y proyecciones.', 'Centro Cultural', false, 'Gratis', '10:00 AM - 8:00 PM', ARRAY['Galerías', 'Talleres', 'Proyecciones', 'Murales en vivo'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9'),

(6, 'Tour Gastronómico del Pacífico', '2026-01-01', '2026-12-31', 'Ruta guiada por mercados y restaurantes. Recursivo todos los sábados.', 'Mercado Alameda', false, '$25.000', '9:00 AM - 1:00 PM', ARRAY['Degustaciones', 'Clases de cocina', 'Visita a mercados', 'Historia gastronómica'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9');

-- Reiniciar secuencias
SELECT setval('eventos_id_seq', (SELECT MAX(id) FROM eventos));