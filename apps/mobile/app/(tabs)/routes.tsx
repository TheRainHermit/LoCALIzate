import { View, Text, ScrollView } from 'react-native';

export default function RoutesScreen() {
  return (
    <ScrollView contentContainerStyle={{ flexGrow: 1, backgroundColor: '#fff8f3', padding: 16 }}>
      <Text style={{ fontSize: 28, fontWeight: '800', marginBottom: 16, color: '#7e5700' }}>
        🛣️ Rutas Inteligentes
      </Text>
      <View style={{ backgroundColor: '#faecdb', padding: 16, borderRadius: 12 }}>
        <Text style={{ fontWeight: '600', marginBottom: 8 }}>Próximamente:</Text>
        <Text>Rutas personalizadas según tu perfil</Text>
      </View>
    </ScrollView>
  );
}