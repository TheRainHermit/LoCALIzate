import { View, Text } from 'react-native';

export default function NotificationBanner({ message }) {
  if (!message) return null;
  return (
    <View style={{ backgroundColor: '#ffb300', padding: 12, borderRadius: 8, marginBottom: 8 }}>
      <Text style={{ color: '#211b11', fontWeight: 'bold' }}>{message}</Text>
    </View>
  );
}