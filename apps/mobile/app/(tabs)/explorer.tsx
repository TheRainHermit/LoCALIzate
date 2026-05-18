import { ScrollView, View, FlatList, TextInput, TouchableOpacity } from 'react-native';
import { useState, useEffect } from 'react';
import { ThemedText, ThemedView, Card, Badge, Colors, Spacing } from '@/components/ui';
import { fetchLugares } from '@/services/apiClient';
import LocationCard from '@/components/LocationCard';

export default function ExplorerScreen() {
  const [lugares, setLugares] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLugares();
  }, []);

  const loadLugares = async () => {
    try {
      const data = await fetchLugares();
      setLugares(data);
      setFiltered(data);
    } catch (error) {
      console.error('Error loading lugares:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (text) => {
    setSearch(text);
    if (text.trim()) {
      const filtered = lugares.filter(
        lugar =>
          lugar.nombre?.toLowerCase().includes(text.toLowerCase()) ||
          lugar.zona?.toLowerCase().includes(text.toLowerCase())
      );
      setFiltered(filtered);
    } else {
      setFiltered(lugares);
    }
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineMD" color="primary">
          ¡Oís, bienvenido!
        </ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
          Explora los mejores lugares de Cali
        </ThemedText>
      </View>

      {/* Search Bar */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <View
          style={{
            flexDirection: 'row',
            alignItems: 'center',
            backgroundColor: Colors.surfaceContainer,
            borderRadius: 12,
            paddingHorizontal: Spacing.md,
            borderWidth: 1,
            borderColor: Colors.outline,
          }}
        >
          <ThemedText style={{ fontSize: 18 }}>🔍</ThemedText>
          <TextInput
            placeholder="Buscar lugares..."
            placeholderTextColor={Colors.onSurfaceVariant}
            value={search}
            onChangeText={handleSearch}
            style={{
              flex: 1,
              paddingHorizontal: Spacing.md,
              paddingVertical: Spacing.md,
              fontSize: 16,
              color: Colors.onSurface,
            }}
          />
        </View>
      </View>

      {/* Lugares List */}
      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
          gap: Spacing.md,
        }}
        scrollEventThrottle={16}
      >
        {loading ? (
          <ThemedText variant="bodyMD" center>
            Cargando lugares...
          </ThemedText>
        ) : filtered.length > 0 ? (
          filtered.map(lugar => (
            <LocationCard key={lugar.id} lugar={lugar} />
          ))
        ) : (
          <Card variant="outlined" style={{ alignItems: 'center', padding: Spacing.lg }}>
            <ThemedText variant="bodyMD" color="onSurfaceVariant">
              No se encontraron lugares
            </ThemedText>
          </Card>
        )}
      </ScrollView>
    </ThemedView>
  );
}