import { View, Text, Button } from 'react-native';

export default function AudioPlayer({ audioUrl }) {
  return (
    <View style={{ marginVertical: 12 }}>
      <Text>Audio guía:</Text>
      <Button title="Reproducir" onPress={() => { /* Lógica de reproducción */ }} />
    </View>
  );
}