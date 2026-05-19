### `database/seeds/lugares.sql`

```sql
-- =====================================================
-- SEED: Lugares Turísticos de Cali
-- =====================================================

-- Limpiar datos existentes (opcional)
-- TRUNCATE TABLE lugares RESTART IDENTITY CASCADE;

-- Insertar lugares turísticos
INSERT INTO lugares (id, nombre, lat, lng, interes, rating, rating_count, horario, precio, direccion, descripcion, tip_caleño, historia, datos_curiosos, imagen, destacado) VALUES
(1, 'Cristo Rey', 3.43587, -76.56490, 'cultura', 4.7, 3200, '6:00 AM - 6:00 PM', 'Gratis', 'Cerro de los Cristales, Siloe', 'Imponente estatua de 26m con vista panorámica de toda Cali.', 'Ve temprano para evitar el sol fuerte y llevar agua.', 'Inaugurado el 25 de octubre de 1953. Obra del escultor Alideo Tazzioli Fontanini.', ARRAY['26 metros de altura', 'Mirador a 1.470 msnm', 'Vista 360° de Cali', 'Se ilumina por las noches'], 'https://images.unsplash.com/photo-1597176394696-79e3223fed37', true),

(2, 'El Gato del Río', 3.45156, -76.54297, 'cultura', 4.5, 2100, '24/7', 'Gratis', 'Paseo Bolívar', 'Famosa escultura de Hernando Tejada. Símbolo de la ciudad.', 'Tómate foto con todos los gatos decorados alrededor.', 'Inaugurada en 1996. Tejada donó la escultura a la ciudad.', ARRAY['12 gatos adicionales decorados', 'Ruta del arte callejero', 'Escultura de 3 metros'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(3, 'Iglesia La Ermita', 3.4520, -76.53201, 'cultura', 4.8, 1500, '8:00 AM - 6:00 PM', 'Gratis', 'Carrera 4 con Calle 13', 'Iglesia de estilo gótico con vitrales impresionantes.', 'Visítala al atardecer para ver los vitrales iluminados.', 'Construida entre 1930 y 1948. Diseñada por el arquitecto belga Agustín Goovaerts.', ARRAY['Vitrales alemanes', 'Torre de 40 metros', 'Órgano centenario'], 'https://images.unsplash.com/photo-1597176394696-79e3223fed37', true),

(4, 'Río Pance', 3.3325, -76.6322, 'naturaleza', 4.6, 8200, '8:00 AM - 5:00 PM', '$5.000', 'Vía a Pance', 'El pulmón natural de Cali con aguas cristalinas.', 'Lleva bloqueador solar, repelente y mucha agua.', 'Zona de reserva natural protegida desde 1980.', ARRAY['Agua cristalina', 'Senderos ecológicos', 'Avistamiento de aves'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(5, 'Bulevar del Río', 3.4533, -76.5325, 'gastronomia', 4.6, 5600, '16:00 - 02:00', 'Varía', 'Carrera 5 entre Calles 7 y 9', 'Epicentro de la vida nocturna caleña.', 'Prueba el cholado y las marranitas.', 'Antigua carrera 5ta convertida en corredor peatonal.', ARRAY['+50 restaurantes', 'Rumba hasta el amanecer', 'Eventos culturales'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(6, 'Zoológico de Cali', 3.4169, -76.5442, 'naturaleza', 4.9, 12400, '9:00 AM - 5:00 PM', '$25.000', 'Calle 14 # 2-00', 'Mejor zoo de Latinoamérica, reconocido mundialmente.', 'Llega temprano para ver los animales activos.', 'Fundado en 1969 por un grupo de amantes de la naturaleza.', ARRAY['+1200 animales', 'Jardín de mariposas', 'Acuario', 'Especies en peligro de extinción'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(7, 'San Antonio', 3.4483, -76.5319, 'cultura', 4.4, 3800, '24/7', 'Gratis', 'Barrio San Antonio', 'Mirador y zona colonial con artesanías locales.', 'Disfruta del atardecer desde el mirador.', 'Barrio tradicional de Cali fundado en el siglo XIX.', ARRAY['Capilla del siglo XVIII', 'Artesanos locales', 'Cafés bohemios'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', false),

(8, 'Plazoleta Jairo Varela', 3.4500, -76.5330, 'salsa', 4.7, 3400, '24/7', 'Gratis', 'Calle 5 con Carrera 4', 'Homenaje al fundador del Grupo Niche.', 'Escucha salsa en vivo los fines de semana.', 'Inaugurada en 2015 en honor al músico caleño.', ARRAY['Estatua de Jairo Varela', 'Salsa en vivo', 'Clases de baile gratis'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(9, 'La Topa Tolondra', 3.4540, -76.5310, 'salsa', 4.9, 8900, '8:00 PM - 3:00 AM', '$20.000+', 'Calle 5 # 13-27', 'Bar icónico de salsa caleña con orquestas en vivo.', 'Reserva con anticipación los fines de semana.', 'Fundado en 1990, punto de encuentro de salseros.', ARRAY['Clases de baile', 'Orquestas en vivo', 'Ambiente auténtico'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true),

(10, 'Morada Ancestral', 3.4200, -76.5400, 'gastronomia', 4.8, 2100, '12:00 PM - 10:00 PM', '$80.000 - $150.000', 'Calle 9 # 48-81, Ciudad Jardín', 'Restaurante top de cocina del Pacífico contemporánea.', 'Prueba el encocado de pescado.', 'Ganador de múltiples premios gastronómicos.', ARRAY['Cocina del Pacífico', 'Ambiente exclusivo', 'Reserva requerida'], 'https://images.unsplash.com/photo-1581519847793-19f9b6e7b5c9', true);

-- Reiniciar secuencias
SELECT setval('lugares_id_seq', (SELECT MAX(id) FROM lugares));