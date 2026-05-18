/**
 * Components Export - Main Entry Point
 * Cali Tourism App
 */

// ==================== UI COMPONENTS & TOKENS ====================
export {
  Button,
  Card,
  Badge,
  ThemedText,
  ThemedView,
  Collapsible,
  IconSymbol,
  Colors,
  Typography,
  Spacing,
  BorderRadius,
  Shadows,
  Breakpoints,
  type ButtonProps,
  type CardProps,
  type BadgeProps,
  type ThemedTextProps,
  type ThemedViewProps,
  type IconSymbolName,
} from './ui';

// ==================== FEATURE COMPONENTS ====================
export { default as LocationCard } from './LocationCard';
export { default as MapViewComponent } from './MapView';  // Cambiar nombre
export { default as ARView } from './ARView';
export { default as AudioPlayer } from './AudioPlayer';
export { default as NotificationBanner } from './NotificationBanner';
export { default as HapticTab } from './HapticTab';
export { default as ExternalLink } from './external-link';

// ==================== SHARED/UTILITY COMPONENTS ====================
export { default as ParallaxScrollView } from './parallax-scroll-view';
export { default as HelloWave } from './hello-wave';