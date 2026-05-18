import { ScrollView, View, Image, Dimensions, TouchableOpacity, FlatList } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing, Typography } from '@/components/ui';
import { AudioPlayer } from '@/components';

interface Lugar {
  id: string;
  nombre: string;
  zona: string;
  descripcion_corta: string;
  descripcion_larga: string;
  imagenes: string[];
  categoria: string;
  rating: number;
  resenas_count: number;
  horario_apertura: string;
  horario_cierre: string;
  entrada_costo: number | null;
  entrada_incluida: boolean;
  telefono: string;
  direccion: string;
  lat: number;
  lng: number;
  audio_guia_url?: string;
  audio_guia_duracion?: string;
  lugares_relacionados: Array<{
    id: string;
    nombre: string;
    distancia: number;
    imagen: string;
  }>;
}

const { width } = Dimensions.get('window');

export default function LugarDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [lugar, setLugar] = useState<Lugar | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);

  useEffect(() => {
    loadLugarDetails();
  }, [id]);

  const loadLugarDetails = async () => {
    try {
      const response = await fetch(`https://tu-api.com/lugares/${id}`);
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setLugar(data);
    } catch (error) {
      console.log('Using mock data for lugar details');
      // Mock data
      const mockLugar: Lugar = {
        id: id || '1',
        nombre: 'Cristo Rey',
        zona: 'San Antonio',
        descripcion_corta: 'Monumento emblemático de Cali',
        descripcion_larga:
          'Cristo Rey es un monumento de gran importancia en Cali. Ubicado en la cima de una colina con vista panorámica a la ciudad. Un lugar perfecto para fotografía y contemplación.',
        imagenes: [
          'https://via.placeholder.com/400x300?text=Cristo+Rey+1',
          'https://via.placeholder.com/400x300?text=Cristo+Rey+2',
          'https://via.placeholder.com/400x300?text=Cristo+Rey+3',
        ],
        categoria: 'Cultura',
        rating: 4.8,
        resenas_count: 234,
        horario_apertura: '06:00 AM',
        horario_cierre: '06:00 PM',
        entrada_costo: null,
        entrada_incluida: true,
        telefono: '+57 2 123 4567',
        direccion: 'Carrera 1, Calle 5, Cali',
        lat: 3.4372,
        lng: -76.5225,
        audio_guia_url: 'https://example.com/audio/cristo-rey.mp3',
        audio_guia_duracion: '5 min',
        lugares_relacionados: [
          {
            id: '2',
            nombre: 'San Antonio',
            distancia: 800,
            imagen: 'https://via.placeholder.com/100?text=San+Antonio',
          },
          {
            id: '3',
            nombre: 'Iglesia San Antonio',
            distancia: 1200,
            imagen: 'https://via.placeholder.com/100?text=Iglesia',
          },
        ],
      };
      setLugar(mockLugar);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigateTo = () => {
    if (lugar) {
      router.push({
        pathname: '/routes/navigate',
        params: {
          destLat: lugar.lat,
          destLng: lugar.lng,
          destName: lugar.nombre,
        },
      });
    }
  };

  const handleRelatedPlace = (placeId: string) => {
    router.push({
      pathname: '/lugar/[id]',
      params: { id: placeId },
    });
  };

  if (loading) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText>Cargando...</ThemedText>
      </ThemedView>
    );
  }

  if (!lugar) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText>Lugar no encontrado</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Galería de fotos */}
        <View>
          <View style={{ width, height: 280, backgroundColor: Colors.surfaceContainerLow, position: 'relative' }}>
            <Image
              source={{ uri: lugar.imagenes[selectedImageIndex] }}
              style={{ width: '100%', height: '100%' }}
              resizeMode="cover"
            />

            {/* Overlay gradient (simulado) */}
            <View
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: 60,
                background: 'linear-gradient(to top, rgba(0,0,0,0.3), transparent)',
              }}
            />

            {/* Indicadores de foto */}
            {lugar.imagenes.length > 1 && (
              <View
                style={{
                  position: 'absolute',
                  bottom: Spacing.md,
                  flexDirection: 'row',
                  gap: Spacing.xs,
                  alignSelf: 'center',
                }}
              >
                {lugar.imagenes.map((_, index) => (
                  <TouchableOpacity
                    key={index}
                    onPress={() => setSelectedImageIndex(index)}
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: selectedImageIndex === index ? Colors.primary : 'rgba(255,255,255,0.5)',
                    }}
                  />
                ))}
              </View>
            )}
          </View>

          {/* Thumbnail preview */}
          {lugar.imagenes.length > 1 && (
            <FlatList
              data={lugar.imagenes}
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.md, gap: Spacing.sm }}
              renderItem={({ item, index }) => (
                <TouchableOpacity
                  onPress={() => setSelectedImageIndex(index)}
                  style={{
                    borderRadius: Spacing.md,
                    overflow: 'hidden',
                    borderWidth: selectedImageIndex === index ? 3 : 0,
                    borderColor: Colors.primary,
                  }}
                >
                  <Image
                    source={{ uri: item }}
                    style={{ width: 80, height: 80 }}
                    resizeMode="cover"
                  />
                </TouchableOpacity>
              )}
              keyExtractor={(_, index) => index.toString()}
              scrollEnabled={lugar.imagenes.length > 4}
            />
          )}
        </View>

        {/* Contenido */}
        <View style={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, gap: Spacing.lg }}>
          {/* Header con título y rating */}
          <View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: Spacing.md }}>
              <View style={{ flex: 1 }}>
                <ThemedText variant="headlineLG" color="onBackground">
                  {lugar.nombre}
                </ThemedText>
                <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                  {lugar.zona}
                </ThemedText>
              </View>
              <Badge label={lugar.categoria} color="primary" size="md" />
            </View>

            {/* Rating */}
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
              <ThemedText style={{ fontSize: 20 }}>⭐</ThemedText>
              <ThemedText variant="titleMD" color="onSurface">
                {lugar.rating.toFixed(1)}
              </ThemedText>
              <ThemedText variant="bodyMD" color="onSurfaceVariant">
                ({lugar.resenas_count} reseñas)
              </ThemedText>
            </View>
          </View>

          {/* Descripción corta */}
          <Card variant="filled">
            <ThemedText variant="bodyMD" color="onSurface">
              {lugar.descripcion_corta}
            </ThemedText>
          </Card>

          {/* Información de entrada */}
          <Card variant="outlined" style={{ borderLeftWidth: 4, borderLeftColor: Colors.tertiary }}>
            <View style={{ gap: Spacing.sm }}>
              <ThemedText variant="titleSM" color="onTertiaryContainer">
                💰 Información de Entrada
              </ThemedText>
              {lugar.entrada_incluida ? (
                <ThemedText variant="bodyMD" color="onSurface">
                  ✅ Entrada Incluida
                </ThemedText>
              ) : lugar.entrada_costo ? (
                <ThemedText variant="bodyMD" color="onSurface">
                  COP ${lugar.entrada_costo.toLocaleString()}
                </ThemedText>
              ) : (
                <ThemedText variant="bodyMD" color="onSurface">
                  Consultar precio
                </ThemedText>
              )}
            </View>
          </Card>

          {/* Horarios */}
          <Card variant="outlined">
            <View style={{ gap: Spacing.md }}>
              <ThemedText variant="titleSM" color="onSurface">
                🕒 Horarios
              </ThemedText>
              <View style={{ gap: Spacing.sm }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <ThemedText variant="bodyMD" color="onSurfaceVariant">
                    Apertura:
                  </ThemedText>
                  <ThemedText variant="bodyMD" color="onSurface" bold>
                    {lugar.horario_apertura}
                  </ThemedText>
                </View>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <ThemedText variant="bodyMD" color="onSurfaceVariant">
                    Cierre:
                  </ThemedText>
                  <ThemedText variant="bodyMD" color="onSurface" bold>
                    {lugar.horario_cierre}
                  </ThemedText>
                </View>
              </View>
            </View>
          </Card>

          {/* Contacto */}
          <Card variant="outlined">
            <View style={{ gap: Spacing.md }}>
              <ThemedText variant="titleSM" color="onSurface">
                📞 Contacto
              </ThemedText>
              <View style={{ gap: Spacing.sm }}>
                <TouchableOpacity>
                  <ThemedText variant="bodyMD" color="primary">
                    {lugar.telefono}
                  </ThemedText>
                </TouchableOpacity>
                <TouchableOpacity>
                  <ThemedText variant="bodyMD" color="primary">
                    📍 {lugar.direccion}
                  </ThemedText>
                </TouchableOpacity>
              </View>
            </View>
          </Card>

          {/* Audio Guía */}
          {lugar.audio_guia_url && (
            <Card variant="filled" style={{ backgroundColor: Colors.primaryContainer }}>
              <View style={{ gap: Spacing.md }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                  <ThemedText style={{ fontSize: 24 }}>🎧</ThemedText>
                  <View style={{ flex: 1 }}>
                    <ThemedText variant="titleSM" color="onPrimaryContainer">
                      Audio Guía
                    </ThemedText>
                    {lugar.audio_guia_duracion && (
                      <ThemedText variant="bodySM" color="onPrimaryContainer">
                        Duración: {lugar.audio_guia_duracion}
                      </ThemedText>
                    )}
                  </View>
                </View>
                <AudioPlayer
                  url={lugar.audio_guia_url}
                  title={`Audio Guía - ${lugar.nombre}`}
                  onPlay={() => setIsAudioPlaying(true)}
                  onPause={() => setIsAudioPlaying(false)}
                />
              </View>
            </Card>
          )}

          {/* Descripción completa */}
          <View>
            <ThemedText variant="titleLG" style={{ marginBottom: Spacing.md }}>
              📖 Más Información
            </ThemedText>
            <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ lineHeight: 24 }}>
              {lugar.descripcion_larga}
            </ThemedText>
          </View>

          {/* Lugares Relacionados */}
          {lugar.lugares_relacionados.length > 0 && (
            <View>
              <ThemedText variant="titleLG" style={{ marginBottom: Spacing.md }}>
                🗺️ Lugares Cercanos
              </ThemedText>
              <FlatList
                data={lugar.lugares_relacionados}
                scrollEnabled={false}
                renderItem={({ item }) => (
                  <TouchableOpacity
                    onPress={() => handleRelatedPlace(item.id)}
                    activeOpacity={0.7}
                    style={{ marginBottom: Spacing.md }}
                  >
                    <Card variant="elevated" style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'center' }}>
                      <Image
                        source={{ uri: item.imagen }}
                        style={{ width: 80, height: 80, borderRadius: Spacing.md }}
                        resizeMode="cover"
                      />
                      <View style={{ flex: 1 }}>
                        <ThemedText variant="bodyMD" color="onSurface">
                          {item.nombre}
                        </ThemedText>
                        <ThemedText variant="labelSM" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                          📍 {item.distancia}m
                        </ThemedText>
                      </View>
                      <ThemedText style={{ fontSize: 20 }}>→</ThemedText>
                    </Card>
                  </TouchableOpacity>
                )}
                keyExtractor={item => item.id}
              />
            </View>
          )}

          {/* Botones de acción */}
          <View style={{ gap: Spacing.md, marginBottom: Spacing.xl }}>
            <Button
              label="📍 Ir Aquí"
              size="lg"
              onPress={handleNavigateTo}
              variant="filled"
            />
            <Button
              label="💬 Ver Reseñas"
              size="lg"
              onPress={() => router.push(`/lugar/${id}/reviews`)}
              variant="outlined"
            />
            <Button
              label="❤️ Guardar"
              size="lg"
              onPress={() => {}}
              variant="tonal"
            />
          </View>
        </View>
      </ScrollView>
    </ThemedView>
  );
}