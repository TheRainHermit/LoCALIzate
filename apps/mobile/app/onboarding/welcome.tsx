import { View, ScrollView, Dimensions, TouchableOpacity, Animated } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useRef, useEffect } from 'react';
import { ThemedView, ThemedText, Button, Colors, Spacing } from '@/components/ui';

interface OnboardingScreen {
  id: string;
  titulo: string;
  descripcion: string;
  emoji: string;
  color: string;
}

const { width } = Dimensions.get('window');

const SCREENS: OnboardingScreen[] = [
  {
    id: '1',
    titulo: '¡Oís, Bienvenido a Cali!',
    descripcion: 'Descubre los lugares más emblemáticos de la Sucursal del Cielo',
    emoji: '🎉',
    color: Colors.primary,
  },
  {
    id: '2',
    titulo: 'Explora con Confianza',
    descripcion: 'Información de seguridad en tiempo real y rutas verificadas',
    emoji: '🛡️',
    color: Colors.tertiary,
  },
  {
    id: '3',
    titulo: 'Gastronomía Caleña',
    descripcion: 'Encuentra auténticos sabores locales y experiencias culinarias',
    emoji: '🍴',
    color: Colors.secondary,
  },
  {
    id: '4',
    titulo: 'Audio Guías Inmersivas',
    descripcion: 'Escucha historias fascinantes de cada lugar',
    emoji: '🎧',
    color: Colors.primary,
  },
  {
    id: '5',
    titulo: 'Crea tu Perfil',
    descripcion: 'Obtén recomendaciones personalizadas según tus intereses',
    emoji: '👤',
    color: Colors.tertiary,
  },
];

export default function WelcomeScreen() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollViewRef = useRef<ScrollView>(null);
  const scrollX = useRef(new Animated.Value(0)).current;

  const handleScroll = Animated.event(
    [{ nativeEvent: { contentOffset: { x: scrollX } } }],
    {
      useNativeDriver: false,
      listener: (event: any) => {
        const contentOffset = event.nativeEvent.contentOffset.x;
        const index = Math.round(contentOffset / width);
        setCurrentIndex(index);
      },
    }
  );

  const handlePrevious = () => {
    if (currentIndex > 0) {
      scrollViewRef.current?.scrollTo({
        x: (currentIndex - 1) * width,
        animated: true,
      });
    }
  };

  const handleNext = () => {
    if (currentIndex < SCREENS.length - 1) {
      scrollViewRef.current?.scrollTo({
        x: (currentIndex + 1) * width,
        animated: true,
      });
    } else {
      router.push('/onboarding/interests');
    }
  };

  const handleSkip = () => {
    router.push('/onboarding/interests');
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header con Skip */}
      <View
        style={{
          flexDirection: 'row',
          justifyContent: 'flex-end',
          paddingHorizontal: Spacing.lg,
          paddingTop: Spacing.lg,
        }}
      >
        {currentIndex < SCREENS.length - 1 && (
          <TouchableOpacity onPress={handleSkip}>
            <ThemedText variant="labelLG" color="primary">
              Saltar
            </ThemedText>
          </TouchableOpacity>
        )}
      </View>

      {/* Carrusel */}
      <ScrollView
        ref={scrollViewRef}
        horizontal
        pagingEnabled
        scrollEventThrottle={16}
        onScroll={handleScroll}
        showsHorizontalScrollIndicator={false}
        style={{ flex: 1 }}
      >
        {SCREENS.map(screen => (
          <View key={screen.id} style={{ width, justifyContent: 'center', alignItems: 'center', paddingHorizontal: Spacing.lg }}>
            <View
              style={{
                width: 140,
                height: 140,
                borderRadius: 70,
                backgroundColor: screen.color,
                justifyContent: 'center',
                alignItems: 'center',
                marginBottom: Spacing.xl,
              }}
            >
              <ThemedText style={{ fontSize: 80 }}>{screen.emoji}</ThemedText>
            </View>

            <ThemedText variant="headlineLG" center style={{ marginBottom: Spacing.md }}>
              {screen.titulo}
            </ThemedText>

            <ThemedText variant="bodyLG" color="onSurfaceVariant" center style={{ marginBottom: Spacing.lg, lineHeight: 28 }}>
              {screen.descripcion}
            </ThemedText>
          </View>
        ))}
      </ScrollView>

      {/* Indicadores (Dots) */}
      <View
        style={{
          flexDirection: 'row',
          justifyContent: 'center',
          gap: Spacing.sm,
          paddingVertical: Spacing.lg,
        }}
      >
        {SCREENS.map((_, index) => (
          <TouchableOpacity
            key={index}
            onPress={() => {
              scrollViewRef.current?.scrollTo({
                x: index * width,
                animated: true,
              });
            }}
            style={{
              width: currentIndex === index ? 32 : 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: currentIndex === index ? Colors.primary : Colors.outline,
            }}
          />
        ))}
      </View>

      {/* Botones */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingBottom: Spacing.xl, gap: Spacing.md }}>
        {currentIndex > 0 && (
          <Button label="← Anterior" variant="outlined" size="md" onPress={handlePrevious} />
        )}
        <Button
          label={currentIndex === SCREENS.length - 1 ? 'Siguiente →' : 'Siguiente →'}
          variant="filled"
          size="lg"
          onPress={handleNext}
        />
      </View>
    </ThemedView>
  );
}