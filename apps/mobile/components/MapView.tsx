import { View, Text } from 'react-native';
import { Colors } from '@/constants';

interface Location {
  id: string;
  nombre: string;
  zona: string;
  descripcion_corta: string;
  lat?: number;
  lng?: number;
  imagen?: string;
}

export default function MapViewComponent({ locations }: { locations: Location[] }) {
  return (
    <View
      style={{
        height: 200,
        backgroundColor: Colors.surfaceContainerLow,
        borderRadius: 16,
        marginBottom: 16,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: Colors.outline,
      }}
    >
      <Text style={{ fontSize: 16, color: Colors.onSurfaceVariant }}>
        🗺️ Mapa Interactivo
      </Text>
      <Text style={{ fontSize: 12, color: Colors.onSurfaceVariant, marginTop: 8 }}>
        {locations.length} lugar{locations.length !== 1 ? 'es' : ''} disponible{locations.length !== 1 ? 's' : ''}
      </Text>
    </View>
  );
}