import { View, Text, ScrollView } from 'react-native';

export default function ExplorerScreen() {
  return (
    <ScrollView contentContainerStyle={{ flexGrow: 1, backgroundColor: '#fff8f3', padding: 16 }}>
      <Text style={{ fontSize: 28, fontWeight: '800', marginBottom: 16, color: '#7e5700' }}>
        ¡Oís, bienvenido!
      </Text>
      <Text style={{ fontSize: 16, color: '#514532', marginBottom: 12 }}>
        Explora los mejores lugares de Cali
      </Text>
      <View style={{ backgroundColor: '#faecdb', padding: 16, borderRadius: 12, marginBottom: 12 }}>
        <Text style={{ fontWeight: '600', marginBottom: 8 }}>Próximamente:</Text>
        <Text>Mapa interactivo con lugares recomendados</Text>
      </View>
    </ScrollView>
  );
}