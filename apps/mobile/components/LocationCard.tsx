import { View, Text, Image } from 'react-native';

export default function LocationCard({ lugar }) {
  return (
    <View style={{ backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8 }}>
      {lugar.imagen && <Image source={{ uri: lugar.imagen }} style={{ width: '100%', height: 120, borderRadius: 12 }} />}
      <Text style={{ fontWeight: 'bold', fontSize: 18, marginTop: 8 }}>{lugar.nombre}</Text>
      <Text style={{ color: '#888', marginTop: 4 }}>{lugar.zona}</Text>
      <Text style={{ marginTop: 4 }}>{lugar.descripcion_corta}</Text>
    </View>
  );
}