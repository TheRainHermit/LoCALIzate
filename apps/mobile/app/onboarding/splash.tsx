import React, { useEffect, useRef } from 'react';
import { View, Image, Animated, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import { Colors, Spacing } from '@/constants';

export default function SplashScreen() {
  const router = useRouter();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Reproducir audio de bienvenida
        const soundObject = new Audio.Sound();
        try {
          // TODO: Cambiar por ruta real del audio de bienvenida
          // await soundObject.loadAsync(require('@/assets/sounds/bienvenida.mp3'));
          // await soundObject.playAsync();
        } catch (error) {
          console.log('Audio de bienvenida no disponible');
        }

        // Animación de fade-in y scale
        Animated.parallel([
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(scaleAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ]).start();

        // Navegar a la siguiente pantalla después de 3 segundos
        const timer = setTimeout(() => {
          router.replace('/onboarding/idioma');
        }, 3500);

        return () => clearTimeout(timer);
      } catch (error) {
        console.error('Error en splash:', error);
      }
    };

    initializeApp();
  }, []);

  return (
    <View
      style={{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: Colors.surface,
      }}
    >
      {/* Logo con animación */}
      <Animated.View
        style={{
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
          marginBottom: Spacing.xl,
        }}
      >
        <Image
          source={require('@/assets/images/localizate.jpeg')}
          style={{
            width: 200,
            height: 200,
            borderRadius: 20,
          }}
          resizeMode="contain"
        />
      </Animated.View>

      {/* Loading indicator */}
      <ActivityIndicator size="large" color={Colors.primary} style={{ marginTop: Spacing.lg }} />
    </View>
  );
}
