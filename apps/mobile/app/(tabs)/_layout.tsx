import { Tabs } from 'expo-router';
import React from 'react';
import { Platform } from 'react-native';

const TAB_ICONS = {
  explorer: '🗺️',
  camera: '📸',
  routes: '🛣️',
  profile: '👤',
};

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#7e5700',
        tabBarInactiveTintColor: '#9a9a9a',
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#fff8f3',
          borderTopColor: '#e5d8c8',
          borderTopWidth: 1,
          paddingBottom: Platform.OS === 'ios' ? 20 : 0,
          height: Platform.OS === 'ios' ? 90 : 60,
        },
      }}
    >
      <Tabs.Screen
        name="explorer"
        options={{
          title: 'Explorador',
          tabBarLabel: 'Explorador',
        }}
      />
      <Tabs.Screen
        name="camera"
        options={{
          title: 'Cámara',
          tabBarLabel: 'Cámara',
        }}
      />
      <Tabs.Screen
        name="routes"
        options={{
          title: 'Rutas',
          tabBarLabel: 'Rutas',
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Perfil',
          tabBarLabel: 'Perfil',
        }}
      />
    </Tabs>
  );
}