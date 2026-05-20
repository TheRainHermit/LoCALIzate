import React, { useRef, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import type { Lugar } from '../../../packages/shared-types';
import { Colors } from '@/constants';

interface LeafletMapViewProps {
  locations: Lugar[];
  userLocation?: { lat: number; lng: number } | null;
  onLocationPress?: (location: Lugar) => void;
  onRouteSelected?: (locations: Lugar[]) => void;
  height?: number;
}

export default function LeafletMapView({
  locations,
  userLocation = null,
  onLocationPress,
  onRouteSelected,
  height = 400,
}: LeafletMapViewProps) {
  const webViewRef = useRef<WebView>(null);
  const [loading, setLoading] = useState(true);

  const handleWebViewMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);

      if (data.type === 'markerClick') {
        const location = locations.find((l) => l.id === data.id);
        if (location) {
          onLocationPress?.(location);
        }
      } else if (data.type === 'routeSelected') {
        const selectedLocations = locations.filter((l) => data.ids.includes(l.id));
        onRouteSelected?.(selectedLocations);
      }
    } catch (error) {
      console.error('Error parsing WebView message:', error);
    }
  };

  const mapHtml = generateLeafletHtml(locations, userLocation);

  return (
    <View style={{ height, backgroundColor: Colors.surfaceContainerLow, borderRadius: 16, overflow: 'hidden' }}>
      {loading && (
        <View
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: Colors.surfaceContainerLow,
            zIndex: 10,
          }}
        >
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      )}

      <WebView
        ref={webViewRef}
        source={{ html: mapHtml }}
        javaScriptEnabled
        domStorageEnabled
        onMessage={handleWebViewMessage}
        onLoadEnd={() => {
          console.log('WebView cargado');
          setLoading(false);
        }}
        onError={(syntheticEvent) => {
          console.error('Error en WebView:', syntheticEvent.nativeEvent);
          setLoading(false);
        }}
        scalePageToFit={false}
        scrollEnabled={true}
        bounces={false}
        style={{ flex: 1, width: '100%', height: '100%' }}
      />
    </View>
  );
}

function generateLeafletHtml(locations: Lugar[], userLocation: any): string {
  const locationsJson = JSON.stringify(
    locations.map((l) => ({
      id: l.id,
      nombre: l.nombre || 'Lugar',
      lat: l.lat,
      lng: l.lng,
      categoria: l.categorias?.[0] || 'default',
      rating: l.rating_promedio || 4.5,
    }))
  );

  const userLocationJson = userLocation ? JSON.stringify(userLocation) : 'null';

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { 
      width: 100%; 
      height: 100%;
      position: fixed;
      top: 0;
      left: 0;
    }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      overflow: hidden;
    }
    #map { 
      position: absolute;
      width: 100%; 
      height: 100%; 
      background: #e5e3df;
      top: 0;
      left: 0;
    }
    .leaflet-container { 
      background: #e5e3df;
      width: 100%;
      height: 100%;
    }
    .leaflet-popup-content-wrapper { 
      border-radius: 8px; 
      font-family: inherit; 
    }
    .leaflet-popup { 
      margin-bottom: 20px; 
    }
    .map-controls {
      position: absolute;
      bottom: 20px;
      left: 20px;
      z-index: 500;
      display: flex;
      gap: 8px;
      background: white;
      padding: 8px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .map-btn {
      padding: 8px 12px;
      background: #FF6B35;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 600;
      font-size: 12px;
      font-family: inherit;
    }
    .map-btn:active {
      opacity: 0.8;
    }
    .leaflet-top, .leaflet-bottom {
      z-index: 400;
    }
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="map-controls">
    <button class="map-btn" id="clearBtn">🗑 Limpiar</button>
    <button class="map-btn" id="centerBtn">🏙 Centro</button>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"><\/script>
  <script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.js"><\/script>
  
  <script>
    const CALI_CENTER = [3.4516, -76.532];
    const categoriaColores = {
      cultura: '#FF6B35',
      naturaleza: '#2ECC71',
      gastronomia: '#E74C3C',
      salsa: '#9B59B6',
      aventura: '#3498DB',
      historia: '#FF8C61',
      musica: '#F7931E',
      arte: '#1ABC9C',
      default: '#95A5A6'
    };

    let map = null;
    let marcadores = [];
    let rutaControl = null;
    let lugaresSeleccionados = [];
    
    const ubicaciones = ${locationsJson};
    const userLocation = ${userLocationJson};

    console.log('Inicializando variables:', { ubicaciones: ubicaciones.length, userLocation });

    function initMap() {
      try {
        console.log('initMap llamada');
        
        const mapDiv = document.getElementById('map');
        console.log('Map div:', mapDiv, 'Size:', mapDiv.offsetWidth, 'x', mapDiv.offsetHeight);
        
        const startLat = userLocation ? userLocation.lat : CALI_CENTER[0];
        const startLng = userLocation ? userLocation.lng : CALI_CENTER[1];
        
        console.log('Creando mapa en:', startLat, startLng);
        
        map = L.map('map', {
          zoomControl: false,
          attributionControl: true
        }).setView([startLat, startLng], 13);
        
        console.log('Mapa creado:', map);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
          attribution: '© OpenStreetMap',
          subdomains: 'abcd',
          maxZoom: 20
        }).addTo(map);
        
        console.log('Tile layer añadido');
        
        L.control.zoom({ position: 'topright' }).addTo(map);
        
        cargarMarcadores();
        
        if (userLocation) {
          const userIcon = L.divIcon({
            html: '<div style="background:#4285F4;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 0 3px #4285F4;"><\/div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8],
            className: ''
          });
          L.marker([userLocation.lat, userLocation.lng], { icon: userIcon, zIndexOffset: 1000 }).addTo(map);
          console.log('User marker añadido');
        }
        
        document.getElementById('clearBtn').onclick = clearRoute;
        document.getElementById('centerBtn').onclick = centerMap;
        
        console.log('✅ Mapa inicializado correctamente');
      } catch (err) {
        console.error('❌ Error inicializando mapa:', err);
      }
    }

    function cargarMarcadores() {
      console.log('Cargando marcadores:', ubicaciones.length);
      
      marcadores.forEach(m => {
        try { map.removeLayer(m); } catch(e) {}
      });
      marcadores = [];

      ubicaciones.forEach(lugar => {
        const color = categoriaColores[lugar.categoria] || categoriaColores.default;
        const iconHtml = '<div style="background:' + color + ';width:32px;height:32px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:16px;">📍<\/div>';
        const icon = L.divIcon({
          html: iconHtml,
          iconSize: [32, 32],
          iconAnchor: [16, 16],
          className: ''
        });
        
        const marker = L.marker([lugar.lat, lugar.lng], { icon: icon }).addTo(map);
        
        const isSelected = lugaresSeleccionados.includes(lugar.id);
        const popupContent = '<div style="font-family:inherit;min-width:180px"><h3 style="margin:0 0 8px;font-size:14px">' + lugar.nombre + '<\/h3><div style="margin-bottom:8px;font-size:12px">⭐ ' + lugar.rating.toFixed(1) + '<\/div><button onclick="toggleLugar(' + lugar.id + ')" style="background:' + (isSelected ? '#2ECC71' : '#FF6B35') + ';color:white;border:none;padding:8px;border-radius:4px;cursor:pointer;font-weight:600;width:100%;font-family:inherit;font-size:12px;">' + (isSelected ? '✓ En ruta' : '+ Agregar') + '<\/button><\/div>';
        
        marker.bindPopup(popupContent);
        marcadores.push(marker);
      });
      console.log('Marcadores cargados:', marcadores.length);
    }

    function toggleLugar(id) {
      const idx = lugaresSeleccionados.indexOf(id);
      if (idx === -1) {
        lugaresSeleccionados.push(id);
      } else {
        lugaresSeleccionados.splice(idx, 1);
      }
      
      cargarMarcadores();
      
      if (lugaresSeleccionados.length >= 2) {
        trazarRuta();
      } else {
        limpiarRuta();
      }
      
      window.ReactNativeWebView.postMessage(JSON.stringify({
        type: 'routeSelected',
        ids: lugaresSeleccionados
      }));
    }

    function trazarRuta() {
      if (lugaresSeleccionados.length < 2) return;

      const waypoints = lugaresSeleccionados.map(id => {
        const lugar = ubicaciones.find(l => l.id === id);
        return L.latLng(lugar.lat, lugar.lng);
      });

      if (rutaControl) {
        try { map.removeControl(rutaControl); } catch(e) {}
      }
      
      rutaControl = L.Routing.control({
        waypoints: waypoints,
        router: L.Routing.osrmv1(),
        routeWhileDragging: false,
        lineOptions: {
          styles: [{ color: '#FF6B35', opacity: 0.8, weight: 4 }]
        },
        createMarker: function() { return null; }
      }).addTo(map);
    }

    function clearRoute() {
      lugaresSeleccionados = [];
      limpiarRuta();
      cargarMarcadores();
      window.ReactNativeWebView.postMessage(JSON.stringify({
        type: 'routeSelected',
        ids: []
      }));
    }

    function limpiarRuta() {
      if (rutaControl) {
        try { map.removeControl(rutaControl); } catch(e) {}
        rutaControl = null;
      }
    }

    function centerMap() {
      map.setView(CALI_CENTER, 13);
    }

    // Esperar a que Leaflet esté listo
    setTimeout(function() {
      console.log('Ejecutando initMap después de delay');
      initMap();
    }, 100);
  <\/script>
</body>
</html>
  `;
}