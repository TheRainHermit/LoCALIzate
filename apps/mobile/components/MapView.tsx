import { View, Text } from 'react-native';
// Puedes usar react-native-maps aquí
export default function MapView({ lugares }) {
  return (
    <View style={{ height: 200, backgroundColor: '#eee', borderRadius: 16, marginBottom: 16, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Mapa (próximamente)</Text>
    </View>
  );
}