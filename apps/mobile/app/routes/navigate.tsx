import { View, ScrollView, TouchableOpacity, Dimensions, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';
import { ThemedView, ThemedText, Card, Button, Colors, Spacing, IconButton } from '@/components/ui';
import { MapViewComponent } from '@/components/MapView';
import { useLocationStore } from '@/store/locationStore';

interface Step {
  id: string;
  instruccion: string;
  distancia: number;
  duracion: number;
  tipo: 'start' | 'turn' | 'arrive';
  icon: string;
}

const { width, height } = Dimensions.get('window');

export default function NavigateScreen() {
  const params = useLocalSearchParams<{
    destLat?: string;
    destLng?: string;
    destName?: string;
  }>();
  const router = useRouter();
  const { setLocation } = useLocationStore();

  const [currentLocation, setCurrentLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [destination] = useState({
    lat: parseFloat(params.destLat || '3.4372'),
    lng: parseFloat(params.destLng || '-76.5225'),
    name: params.destName || 'Destino',
  });

  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalDistance, setTotalDistance] = useState(0);
  const [totalTime, setTotalTime] = useState(0);
  const [isNavigating, setIsNavigating] = useState(false);
  const [loading, setLoading] = useState(true);

  // Ejemplo de ruta
  const EXAMPLE_STEPS: Step[] = [
    {
      id: '1',
      instruccion: 'Comienza en tu ubicación actual',
      distancia: 0,
      duracion: 0,
      tipo: 'start',
      icon: '📍',
    },
    {
      id: '2',
      instruccion: 'Dirígete al norte por Calle 5',
      distancia: 450,
      duracion: 6,
      tipo: 'turn',
      icon: '↑',
    },
    {
      id: '3',
      instruccion: 'Gira a la derecha en Carrera 15',
      distancia: 320,
      duracion: 4,
      tipo: 'turn',
      icon: '→',
    },
    {
      id: '4',
      instruccion: 'Continúa recto 280 metros',
      distancia: 280,
      duracion: 3,
      tipo: 'turn',
      icon: '↑',
    },
    {
      id: '5',
      instruccion: 'Gira a la izquierda',
      distancia: 120,
      duracion: 2,
      tipo: 'turn',
      icon: '←',
    },
    {
      id: '6',
      instruccion: 'Has llegado a tu destino',
      distancia: 0,
      duracion: 0,
      tipo: 'arrive',
      icon: '🎉',
    },
  ];

  useEffect(() => {
    initializeNavigation();
  }, []);

  const initializeNavigation = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permiso denegado', 'Se necesita acceso a la ubicación para navegar');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      const current = {
        lat: location.coords.latitude,
        lng: location.coords.longitude,
      };

      setCurrentLocation(current);
      setLocation(current);

      // Calcular ruta (en producción usar API real como Google Maps)
      calculateRoute(current);

      setSteps(EXAMPLE_STEPS);
      setTotalDistance(1450); // metros
      setTotalTime(18); // minutos
    } catch (error) {
      console.error('Error initializing navigation:', error);
      Alert.alert('Error', 'No se pudo obtener tu ubicación');
    } finally {
      setLoading(false);
    }
  };

  const calculateRoute = (origin: { lat: number; lng: number }) => {
    try {
      // En producción, aquí iría una llamada a Google Maps Directions API
      console.log(`Calculando ruta desde ${origin.lat}, ${origin.lng}`);
    } catch (error) {
      console.warn('Error calculating route:', error);
    }
  };

  const handleStartNavigation = () => {
    setIsNavigating(true);
  };

  const handleStopNavigation = () => {
    setIsNavigating(false);
    setCurrentStep(0);
  };

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (loading) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText variant="bodyMD">Inicializando navegación...</ThemedText>
      </ThemedView>
    );
  }

  const currentStepData = steps[currentStep];
  const remainingDistance = totalDistance - steps.slice(0, currentStep).reduce((acc, s) => acc + s.distancia, 0);
  const remainingTime = Math.ceil(remainingDistance / 75); // ~75m por minuto

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Mapa */}
      <View style={{ height: isNavigating ? height * 0.6 : height * 0.35, width: '100%' }}>
        <MapViewComponent
            locations={
                currentLocation
                ? [
                    {
                        id: 'current',
                        nombre: 'Tu ubicación',
                        zona: 'Actual',
                        descripcion_corta: '',
                        lat: currentLocation.lat,
                        lng: currentLocation.lng,
                    },
                    {
                        id: 'destination',
                        nombre: destination.name,
                        zona: 'Destino',
                        descripcion_corta: '',
                        lat: destination.lat,
                        lng: destination.lng,
                    },
                    ]
                : []
            }
            />
      </View>

      {/* Info Principal */}
      {isNavigating ? (
        <ScrollView style={{ flex: 1 }} scrollEnabled={false}>
          <View style={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, gap: Spacing.lg }}>
            {/* Destino */}
            <Card variant="filled" style={{ backgroundColor: Colors.primaryContainer }}>
              <ThemedText variant="titleLG" color="onPrimaryContainer">
                {destination.name}
              </ThemedText>
              <View style={{ marginTop: Spacing.md, flexDirection: 'row', gap: Spacing.lg, alignItems: 'center' }}>
                <View>
                  <ThemedText variant="labelSM" color="onPrimaryContainer">
                    Distancia Restante
                  </ThemedText>
                  <ThemedText variant="headlineLG" color="onPrimaryContainer">
                    {(remainingDistance / 1000).toFixed(1)}km
                  </ThemedText>
                </View>
                <View>
                  <ThemedText variant="labelSM" color="onPrimaryContainer">
                    Tiempo Estimado
                  </ThemedText>
                  <ThemedText variant="headlineLG" color="onPrimaryContainer">
                    {remainingTime}min
                  </ThemedText>
                </View>
              </View>
            </Card>

            {/* Instrucción Actual */}
            <Card variant="elevated" style={{ borderLeftWidth: 6, borderLeftColor: Colors.secondary, padding: Spacing.lg }}>
              <View style={{ gap: Spacing.md }}>
                <View style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'center' }}>
                  <View
                    style={{
                      width: 60,
                      height: 60,
                      borderRadius: 30,
                      backgroundColor: Colors.secondaryContainer,
                      justifyContent: 'center',
                      alignItems: 'center',
                    }}
                  >
                    <ThemedText style={{ fontSize: 28 }}>{currentStepData.icon}</ThemedText>
                  </View>
                  <View style={{ flex: 1 }}>
                    <ThemedText variant="titleMD" color="onSurface">
                      {currentStepData.instruccion}
                    </ThemedText>
                    {currentStepData.distancia > 0 && (
                      <ThemedText variant="labelSM" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                        {currentStepData.distancia}m • {currentStepData.duracion}min
                      </ThemedText>
                    )}
                  </View>
                </View>
              </View>
            </Card>

            {/* Siguientes pasos */}
            {currentStep < steps.length - 2 && (
              <View>
                <ThemedText variant="titleSM" color="onSurfaceVariant" style={{ marginBottom: Spacing.md }}>
                  Próximos pasos
                </ThemedText>
                {steps
                  .slice(currentStep + 1, currentStep + 3)
                  .map((step, index) => (
                    <Card key={step.id} variant="filled" style={{ marginBottom: Spacing.sm, paddingVertical: Spacing.md }}>
                      <View style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'center' }}>
                        <ThemedText style={{ fontSize: 24 }}>{step.icon}</ThemedText>
                        <View style={{ flex: 1 }}>
                          <ThemedText variant="bodySM" color="onSurface">
                            {step.instruccion}
                          </ThemedText>
                        </View>
                      </View>
                    </Card>
                  ))}
              </View>
            )}

            {/* Botones */}
            <View style={{ flexDirection: 'row', gap: Spacing.md, marginTop: Spacing.lg }}>
              <TouchableOpacity
                style={{
                  flex: 1,
                  paddingVertical: Spacing.md,
                  borderRadius: 12,
                  backgroundColor: Colors.surfaceContainer,
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
                onPress={handlePreviousStep}
                disabled={currentStep === 0}
              >
                <ThemedText variant="labelLG" color={currentStep === 0 ? 'onSurfaceVariant' : 'onSurface'}>
                  ← Anterior
                </ThemedText>
              </TouchableOpacity>

              {currentStep < steps.length - 1 ? (
                <TouchableOpacity
                  style={{
                    flex: 1,
                    paddingVertical: Spacing.md,
                    borderRadius: 12,
                    backgroundColor: Colors.primary,
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                  onPress={handleNextStep}
                >
                  <ThemedText variant="labelLG" color="onPrimary">
                    Siguiente →
                  </ThemedText>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity
                  style={{
                    flex: 1,
                    paddingVertical: Spacing.md,
                    borderRadius: 12,
                    backgroundColor: Colors.tertiary,
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                  onPress={handleStopNavigation}
                >
                  <ThemedText variant="labelLG" color="onTertiary">
                    ✓ Finalizar
                  </ThemedText>
                </TouchableOpacity>
              )}
            </View>

            <Button label="Cancelar Navegación" variant="outlined" onPress={handleStopNavigation} />
          </View>
        </ScrollView>
      ) : (
        <ScrollView style={{ flex: 1 }}>
          <View style={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, gap: Spacing.lg }}>
            {/* Resumen */}
            <Card variant="elevated">
              <ThemedText variant="titleLG" color="onSurface">
                {destination.name}
              </ThemedText>
              <View style={{ marginTop: Spacing.lg, gap: Spacing.md }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <ThemedText variant="labelMD" color="onSurfaceVariant">
                    Distancia Total
                  </ThemedText>
                  <ThemedText variant="headlineMD" color="primary">
                    {(totalDistance / 1000).toFixed(1)}km
                  </ThemedText>
                </View>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <ThemedText variant="labelMD" color="onSurfaceVariant">
                    Tiempo Estimado
                  </ThemedText>
                  <ThemedText variant="headlineMD" color="primary">
                    {totalTime}min
                  </ThemedText>
                </View>
              </View>
            </Card>

            {/* Lista de Pasos */}
            <View>
              <ThemedText variant="titleLG" style={{ marginBottom: Spacing.md }}>
                Ruta
              </ThemedText>
              {steps.map((step, index) => (
                <TouchableOpacity
                  key={step.id}
                  onPress={() => {
                    setCurrentStep(index);
                    setIsNavigating(true);
                  }}
                  activeOpacity={0.7}
                  style={{ marginBottom: Spacing.sm }}
                >
                  <Card variant={index === currentStep ? 'filled' : 'outlined'}>
                    <View style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'center' }}>
                      <View
                        style={{
                          width: 44,
                          height: 44,
                          borderRadius: 22,
                          backgroundColor: Colors.primaryContainer,
                          justifyContent: 'center',
                          alignItems: 'center',
                        }}
                      >
                        <ThemedText style={{ fontSize: 20 }}>{step.icon}</ThemedText>
                      </View>
                      <View style={{ flex: 1 }}>
                        <ThemedText variant="bodyMD" color="onSurface">
                          {step.instruccion}
                        </ThemedText>
                        {step.distancia > 0 && (
                          <ThemedText variant="labelSM" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                            {step.distancia}m
                          </ThemedText>
                        )}
                      </View>
                      <ThemedText style={{ fontSize: 16 }}>{step.duracion > 0 ? `${step.duracion}m` : ''}</ThemedText>
                    </View>
                  </Card>
                </TouchableOpacity>
              ))}
            </View>

            {/* CTA */}
            <Button
              label="🧭 Iniciar Navegación"
              size="lg"
              onPress={handleStartNavigation}
              style={{ marginTop: Spacing.lg }}
            />
          </View>
        </ScrollView>
      )}
    </ThemedView>
  );
}