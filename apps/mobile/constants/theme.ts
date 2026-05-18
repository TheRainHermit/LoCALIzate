/**
 * Theme configuration - LoCALIzate
 */

import { Platform } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from './designTokens';

export const useTheme = () => ({
  colors: Colors,
  typography: Typography,
  spacing: Spacing,
  borderRadius: BorderRadius,
});

// Para compatibilidad con código existente
export const Fonts = Platform.select({
  ios: {
    sans: 'Plus Jakarta Sans',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  default: {
    sans: 'Plus Jakarta Sans',
    serif: 'serif',
    rounded: 'Plus Jakarta Sans',
    mono: 'monospace',
  },
  web: {
    sans: "'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'Plus Jakarta Sans', 'SF Pro Rounded', sans-serif",
    mono: "'Courier New', monospace",
  },
});

export const LegacyColors = {
  light: {
    text: Colors.onBackground,
    background: Colors.background,
    tint: Colors.primary,
    icon: Colors.onSurfaceVariant,
    tabIconDefault: Colors.onSurfaceVariant,
    tabIconSelected: Colors.primary,
  },
  dark: {
    text: Colors.surface,
    background: Colors.inverseSurface,
    tint: Colors.inversePrimary,
    icon: Colors.onSurfaceVariant,
    tabIconDefault: Colors.onSurfaceVariant,
    tabIconSelected: Colors.inversePrimary,
  },
};