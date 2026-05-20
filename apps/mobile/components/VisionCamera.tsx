import React, { useRef, useState, useEffect } from 'react';
import { View, TouchableOpacity, Text, ActivityIndicator, Alert, Modal } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Colors, Spacing } from '@/constants';
import { detectMonument } from '@/services/visionService';
import type { VisionResult } from '@/services/visionService';

interface VisionCameraProps {
  isVisible: boolean;
  onClose: () => void;
  onDetected?: (result: VisionResult) => void;
}

export default function VisionCamera({ isVisible, onClose, onDetected }: VisionCameraProps) {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    if (isVisible && !permission?.granted) {
      requestPermission();
    }
  }, [isVisible]);

  const takePicture = async () => {
    if (!cameraRef.current) return;

    try {
      setIsCapturing(true);
      const photo = await cameraRef.current.takePictureAsync({ base64: false });

      console.log('📸 Foto capturada:', photo.uri);

      // Detectar monumento
      const detectionResult = await detectMonument(photo.uri);
      onDetected?.(detectionResult);

      // Cerrar cámara después de detectar
      setTimeout(() => {
        onClose();
      }, 500);
    } catch (error) {
      console.error('Error capturando foto:', error);
      Alert.alert('Error', 'No se pudo capturar la foto');
    } finally {
      setIsCapturing(false);
    }
  };

  if (!permission?.granted) {
    return (
      <Modal visible={isVisible} animationType="slide">
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: Colors.background }}>
          <Text style={{ fontSize: 16, marginBottom: Spacing.lg, color: Colors.onBackground }}>
            Se necesita permiso de cámara
          </Text>
          <TouchableOpacity
            onPress={requestPermission}
            style={{
              paddingVertical: Spacing.md,
              paddingHorizontal: Spacing.lg,
              backgroundColor: Colors.primary,
              borderRadius: 8,
            }}
          >
            <Text style={{ color: 'white', fontWeight: '600' }}>Permitir acceso</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={onClose}
            style={{ marginTop: Spacing.lg, paddingVertical: Spacing.md }}
          >
            <Text style={{ color: Colors.primary, fontWeight: '600' }}>Cerrar</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    );
  }

  return (
    <Modal visible={isVisible} animationType="slide">
      <View style={{ flex: 1, backgroundColor: '#000', position: 'relative' }}>
        <CameraView ref={cameraRef} style={{ flex: 1 }} facing="back" />

        {/* Overlay de captura - FUERA del CameraView */}
        <View
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            justifyContent: 'space-between',
            paddingTop: Spacing.lg,
            paddingBottom: Spacing.xl,
            pointerEvents: 'box-none',
          }}
        >
          {/* Header */}
          <View style={{ paddingHorizontal: Spacing.lg, zIndex: 10 }}>
            <TouchableOpacity onPress={onClose}>
              <Text style={{ fontSize: 28, color: 'white' }}>←</Text>
            </TouchableOpacity>
          </View>

          {/* Centro - Instrucciones */}
          <View style={{ alignItems: 'center', gap: Spacing.md, zIndex: 10 }}>
            <View
              style={{
                width: 200,
                height: 200,
                borderRadius: 100,
                borderWidth: 3,
                borderColor: Colors.primary,
                opacity: 0.6,
              }}
            />
            <Text style={{ fontSize: 14, color: 'white', textAlign: 'center', paddingHorizontal: Spacing.lg }}>
              Apunta al monumento o lugar emblemático
            </Text>
          </View>

          {/* Bottom - Botones */}
          <View
            style={{
              flexDirection: 'row',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingHorizontal: Spacing.lg,
              zIndex: 10,
            }}
          >
            <TouchableOpacity onPress={onClose}>
              <Text style={{ fontSize: 20, color: 'rgba(255,255,255,0.5)' }}>✕</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={takePicture}
              disabled={isCapturing}
              style={{
                width: 70,
                height: 70,
                borderRadius: 35,
                backgroundColor: Colors.primary,
                justifyContent: 'center',
                alignItems: 'center',
                opacity: isCapturing ? 0.5 : 1,
              }}
            >
              {isCapturing ? (
                <ActivityIndicator size="large" color="white" />
              ) : (
                <View
                  style={{
                    width: 56,
                    height: 56,
                    borderRadius: 28,
                    borderWidth: 2,
                    borderColor: 'white',
                  }}
                />
              )}
            </TouchableOpacity>

            <View style={{ width: 30 }} />
          </View>
        </View>
      </View>
    </Modal>
  );
}