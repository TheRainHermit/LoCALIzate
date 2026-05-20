import { ScrollView, View, Image, Dimensions, TouchableOpacity, FlatList, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing, Typography } from '@/components/ui';
import { fetchLugarDetail, fetchLugarResenas } from '@/services/apiClient';
import type { Lugar } from '../../../../packages/shared-types';

const { width } = Dimensions.get('window');

export default function LugarDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [lugar, setLugar] = useState<Lugar | null>(null);
  const [resenas, setResenas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  useEffect(() => {
    if (id) {
      loadLugarDetails();
    }
  }, [id]);

  const loadLugarDetails = async () => {
    try {
      setLoading(true);
      const lugarId = parseInt(id as string);
      
      // Cargar lugar y reseñas en paralelo
      const [lugarData, resenasData] = await Promise.all([
        fetchLugarDetail(lugarId),
        fetchLugarResenas(lugarId),
      ]);
      
      setLugar(lugarData);
      setResenas(resenasData || []);
    } catch (error) {
      console.error('Error cargando lugar:', error);
      Alert.alert('Error', 'No se pudo cargar los detalles del lugar');
      router.back();
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </ThemedView>
    );
  }

  if (!lugar) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText variant="bodyMD">No se encontró el lugar</ThemedText>
      </ThemedView>
    );
  }

  const imagenes = lugar.galeria_imagenes || [lugar.imagen_principal];

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Galería */}
        <View style={{ height: 280, backgroundColor: Colors.surfaceContainer, position: 'relative' }}>
          <Image
            source={{ uri: imagenes[selectedImageIndex] || 'https://via.placeholder.com/400x300?text=Sin+Imagen' }}
            style={{ width: '100%', height: '100%' }}
            resizeMode="cover"
          />
          
          {/* Indicador de imágenes */}
          {imagenes.length > 1 && (
            <View style={{ position: 'absolute', bottom: Spacing.md, left: Spacing.md, flexDirection: 'row', gap: Spacing.xs }}>
              {imagenes.map((_, idx) => (
                <TouchableOpacity
                  key={idx}
                  onPress={() => setSelectedImageIndex(idx)}
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: idx === selectedImageIndex ? Colors.primary : 'rgba(255,255,255,0.5)',
                  }}
                />
              ))}
            </View>
          )}

          {/* Botón cerrar */}
          <TouchableOpacity
            onPress={() => router.back()}
            style={{
              position: 'absolute',
              top: Spacing.lg,
              right: Spacing.lg,
              width: 40,
              height: 40,
              borderRadius: 20,
              backgroundColor: 'rgba(0,0,0,0.3)',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <ThemedText style={{ fontSize: 24 }}>✕</ThemedText>
          </TouchableOpacity>
        </View>

        {/* Contenido */}
        <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg, gap: Spacing.lg }}>
          {/* Título y rating */}
          <View>
            <ThemedText variant="headlineLG">{lugar.nombre}</ThemedText>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginTop: Spacing.xs }}>
              <ThemedText style={{ fontSize: 16 }}>⭐ {lugar.rating_promedio?.toFixed(1) || '4.5'}</ThemedText>
              <ThemedText variant="labelSM" color="onSurfaceVariant">
                ({lugar.resenas_count} reseñas)
              </ThemedText>
            </View>
            <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.sm }}>
              {lugar.zona}
            </ThemedText>
          </View>

          {/* Descripción */}
          <ThemedText variant="bodyMD">{lugar.descripcion}</ThemedText>

          {/* Info Cards */}
          <View style={{ gap: Spacing.md }}>
            {lugar.entrada_pagada && (
              <Card variant="filled">
                <ThemedText variant="labelMD">💰 Entrada</ThemedText>
                <ThemedText variant="headlineMD" color="primary" style={{ marginTop: Spacing.xs }}>
                  ${lugar.costo_entrada?.toLocaleString() || 'Consultar'}
                </ThemedText>
              </Card>
            )}

            {lugar.horario_atencion?.lunes_a_viernes && (
              <Card variant="filled">
                <ThemedText variant="labelMD">🕒 Horarios</ThemedText>
                <ThemedText variant="bodySM" style={{ marginTop: Spacing.xs }}>
                  {lugar.horario_atencion.lunes_a_viernes.apertura} - {lugar.horario_atencion.lunes_a_viernes.cierre}
                </ThemedText>
              </Card>
            )}

            {lugar.contacto?.telefono && (
              <Card variant="filled">
                <ThemedText variant="labelMD">📞 Teléfono</ThemedText>
                <ThemedText variant="bodySM" style={{ marginTop: Spacing.xs }}>
                  {lugar.contacto.telefono}
                </ThemedText>
              </Card>
            )}

            {lugar.contacto?.sitio_web && (
              <Card variant="filled">
                <ThemedText variant="labelMD">🌐 Sitio Web</ThemedText>
                <ThemedText variant="bodySM" color="primary" style={{ marginTop: Spacing.xs }}>
                  {lugar.contacto.sitio_web}
                </ThemedText>
              </Card>
            )}
          </View>

          {/* Audio guía */}
          {lugar.audio_guia && (
            <Card variant="elevated" style={{ borderLeftWidth: 4, borderLeftColor: Colors.secondary }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
                <ThemedText style={{ fontSize: 28 }}>🎧</ThemedText>
                <View style={{ flex: 1 }}>
                  <ThemedText variant="titleMD">Audio Guía Disponible</ThemedText>
                  <ThemedText variant="labelSM" color="onSurfaceVariant">
                    Escucha la historia de este lugar
                  </ThemedText>
                </View>
              </View>
            </Card>
          )}

          {/* Tip caleño */}
          {lugar.tip_caleño && (
            <Card variant="filled" style={{ backgroundColor: Colors.primaryContainer }}>
              <ThemedText variant="labelLG" color="onPrimaryContainer">
                💡 Consejo Local:
              </ThemedText>
              <ThemedText variant="bodySM" color="onPrimaryContainer" style={{ marginTop: Spacing.sm }}>
                {lugar.tip_caleño}
              </ThemedText>
            </Card>
          )}

          {/* Datos curiosos */}
          {lugar.datos_curiosos && lugar.datos_curiosos.length > 0 && (
            <View>
              <ThemedText variant="titleMD" style={{ marginBottom: Spacing.md }}>
                🤓 Datos Curiosos
              </ThemedText>
              {lugar.datos_curiosos.map((dato, idx) => (
                <Card key={idx} variant="filled" style={{ marginBottom: Spacing.sm }}>
                  <ThemedText variant="bodySM">• {dato}</ThemedText>
                </Card>
              ))}
            </View>
          )}

          {/* Reviews */}
          {resenas.length > 0 && (
            <View>
              <ThemedText variant="titleMD" style={{ marginBottom: Spacing.md }}>
                📝 Reseñas
              </ThemedText>
              {resenas.slice(0, 3).map((resena, idx) => (
                <Card key={idx} variant="filled" style={{ marginBottom: Spacing.sm }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.sm }}>
                    <ThemedText variant="labelMD">{resena.usuario_nombre || 'Usuario'}</ThemedText>
                    <ThemedText style={{ fontSize: 14 }}>⭐ {resena.rating}</ThemedText>
                  </View>
                  <ThemedText variant="bodySM">{resena.comentario}</ThemedText>
                  <ThemedText variant="labelSM" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                    {new Date(resena.created_at).toLocaleDateString()}
                  </ThemedText>
                </Card>
              ))}
              
              {resenas.length > 3 && (
                <Button
                  label="Ver todas las reseñas"
                  variant="text"
                  onPress={() => router.push(`/lugar/${lugar.id}/reviews`)}
                />
              )}
            </View>
          )}

          {/* CTAs */}
          <View style={{ gap: Spacing.md, marginBottom: Spacing.lg }}>
            <Button label="🧭 Ir Aquí" size="lg" />
            <Button label="❤️ Guardar" variant="outlined" size="lg" />
          </View>
        </View>
      </ScrollView>
    </ThemedView>
  );
}