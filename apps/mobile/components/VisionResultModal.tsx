import React from 'react';
import { View, TouchableOpacity, Text, Modal, ScrollView, Image } from 'react-native';
import { Colors, Spacing } from '@/constants';
import type { VisionResult } from '@/services/visionService';

interface VisionResultModalProps {
  isVisible: boolean;
  result: VisionResult | null;
  onClose: () => void;
  onAddToRoute?: () => void;
}

export default function VisionResultModal({
  isVisible,
  result,
  onClose,
  onAddToRoute,
}: VisionResultModalProps) {
  if (!result) return null;

  return (
    <Modal visible={isVisible} animationType="slide" transparent>
      <View
        style={{
          flex: 1,
          backgroundColor: 'rgba(0,0,0,0.5)',
          justifyContent: 'flex-end',
        }}
      >
        <View
          style={{
            backgroundColor: Colors.surface,
            borderTopLeftRadius: 24,
            borderTopRightRadius: 24,
            maxHeight: '80%',
            paddingTop: Spacing.md,
          }}
        >
          {/* Handle bar */}
          <View
            style={{
              alignSelf: 'center',
              width: 40,
              height: 4,
              borderRadius: 2,
              backgroundColor: Colors.onSurfaceVariant,
              marginBottom: Spacing.lg,
            }}
          />

          <ScrollView
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: Spacing.xl }}
          >
            {result.success && result.lugar ? (
              <>
                {/* Imagen */}
                {result.lugar.imagen_url && (
                  <Image
                    source={{ uri: result.lugar.imagen_url }}
                    style={{
                      width: '100%',
                      height: 200,
                      marginBottom: Spacing.lg,
                    }}
                  />
                )}

                {/* Confianza */}
                {result.confidence && (
                  <View style={{ paddingHorizontal: Spacing.lg, marginBottom: Spacing.md }}>
                    <Text style={{ fontSize: 12, color: Colors.onSurfaceVariant }}>
                      Coincidencia: {(result.confidence * 100).toFixed(0)}%
                    </Text>
                  </View>
                )}

                {/* Titulo */}
                <Text
                  style={{
                    fontSize: 24,
                    fontWeight: '700',
                    color: Colors.onSurface,
                    paddingHorizontal: Spacing.lg,
                    marginBottom: Spacing.md,
                  }}
                >
                  {result.lugar.nombre}
                </Text>

                {/* Zona */}
                <Text
                  style={{
                    fontSize: 14,
                    color: Colors.onSurfaceVariant,
                    paddingHorizontal: Spacing.lg,
                    marginBottom: Spacing.lg,
                  }}
                >
                  📍 {result.lugar.zona}
                </Text>

                {/* Rating */}
                <View
                  style={{
                    flexDirection: 'row',
                    alignItems: 'center',
                    paddingHorizontal: Spacing.lg,
                    marginBottom: Spacing.lg,
                  }}
                >
                  <Text style={{ fontSize: 16 }}>⭐ {result.lugar.rating_promedio}</Text>
                </View>

                {/* Descripción */}
                <Text
                  style={{
                    fontSize: 14,
                    color: Colors.onSurface,
                    lineHeight: 22,
                    paddingHorizontal: Spacing.lg,
                    marginBottom: Spacing.lg,
                  }}
                >
                  {result.lugar.descripcion}
                </Text>

                {/* Mensaje caleño */}
                {result.mensaje_caleño && (
                  <View
                    style={{
                      marginHorizontal: Spacing.lg,
                      marginBottom: Spacing.lg,
                      padding: Spacing.md,
                      backgroundColor: Colors.primaryContainer,
                      borderRadius: 12,
                      borderLeftWidth: 4,
                      borderLeftColor: Colors.primary,
                    }}
                  >
                    <Text
                      style={{
                        fontSize: 13,
                        color: Colors.onPrimaryContainer,
                        fontWeight: '600',
                      }}
                    >
                      💬 {result.mensaje_caleño}
                    </Text>
                  </View>
                )}

                {/* Botones */}
                <View
                  style={{
                    flexDirection: 'row',
                    gap: Spacing.md,
                    paddingHorizontal: Spacing.lg,
                  }}
                >
                  <TouchableOpacity
                    onPress={onAddToRoute}
                    style={{
                      flex: 1,
                      paddingVertical: Spacing.md,
                      backgroundColor: Colors.primary,
                      borderRadius: 8,
                      alignItems: 'center',
                    }}
                  >
                    <Text style={{ color: 'white', fontWeight: '600' }}>+ Agregar a ruta</Text>
                  </TouchableOpacity>
                </View>
              </>
            ) : (
              <>
                {/* Error */}
                <View style={{ alignItems: 'center', paddingHorizontal: Spacing.lg }}>
                  <Text style={{ fontSize: 20, marginBottom: Spacing.md }}>🤔</Text>
                  <Text
                    style={{
                      fontSize: 16,
                      fontWeight: '600',
                      color: Colors.onSurface,
                      marginBottom: Spacing.md,
                      textAlign: 'center',
                    }}
                  >
                    {result.message || 'No pude identificar lo que estás mirando'}
                  </Text>
                  <Text
                    style={{
                      fontSize: 13,
                      color: Colors.onSurfaceVariant,
                      textAlign: 'center',
                      marginBottom: Spacing.lg,
                    }}
                  >
                    Intenta con mejor iluminación o más cerca del monumento
                  </Text>
                </View>
              </>
            )}
          </ScrollView>

          {/* Cerrar */}
          <TouchableOpacity
            onPress={onClose}
            style={{
              paddingVertical: Spacing.md,
              alignItems: 'center',
              borderTopWidth: 1,
              borderTopColor: Colors.outlineVariant,
              paddingHorizontal: Spacing.lg,
            }}
          >
            <Text style={{ color: Colors.primary, fontWeight: '600', fontSize: 16 }}>
              Cerrar
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}