import { View, Text, TouchableOpacity } from 'react-native';

export default function CameraScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff8f3' }}>
      <Text style={{ fontSize: 28, fontWeight: '800', marginBottom: 16, color: '#7e5700' }}>
        📸 Reconocimiento Visual
      </Text>
      <TouchableOpacity style={{ backgroundColor: '#7e5700', padding: 16, borderRadius: 12 }}>
        <Text style={{ color: '#fff', fontWeight: '600', fontSize: 16 }}>Abrir cámara</Text>
      </TouchableOpacity>
      <Text style={{ marginTop: 20, color: '#514532' }}>
        Apunta a un monumento para saber más
      </Text>
    </View>
  );
}