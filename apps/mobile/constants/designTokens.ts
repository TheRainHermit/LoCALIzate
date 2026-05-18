/**
 * Design System Tokens - Cali Tourism App
 * Based on Material Design 3 - Cali Tourism Design System
 */

import { Platform } from 'react-native';

// ==================== COLORS ====================
export const Colors = {
  // Primary (Marrón cálido - identidad Cali)
  primary: '#7e5700',
  onPrimary: '#ffffff',
  primaryContainer: '#ffb300',
  onPrimaryContainer: '#6b4900',
  inversePrimary: '#ffba38',

  // Secondary (Rojo - pasión)
  secondary: '#bb0020',
  onSecondary: '#ffffff',
  secondaryContainer: '#e12634',
  onSecondaryContainer: '#fffbff',

  // Tertiary (Verde - naturaleza)
  tertiary: '#2c694e',
  onTertiary: '#ffffff',
  tertiaryContainer: '#90cfae',
  onTertiaryContainer: '#1a5a40',

  // Surface (Fondo principal - cream)
  surface: '#fff8f3',
  surfaceContainer: '#faecdb',
  surfaceContainerLow: '#fff2e2',
  surfaceContainerHigh: '#f4e6d6',
  surfaceContainerHighest: '#eee0d0',
  onSurface: '#211b11',
  onSurfaceVariant: '#514532',

  // Other
  background: '#fff8f3',
  onBackground: '#211b11',
  surfaceVariant: '#eee0d0',
  outline: '#847560',
  outlineVariant: '#d6c4ac',
  inverseSurface: '#372f24',
  inverseOnSurface: '#fdefde',

  // Error
  error: '#ba1a1a',
  onError: '#ffffff',
  errorContainer: '#ffdad6',
  onErrorContainer: '#93000a',
};

// ==================== TYPOGRAPHY ====================
export const Typography = {
  headlineXL: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 40,
    fontWeight: '800' as const,
    lineHeight: 48,
    letterSpacing: -0.8, // -0.02em
  },
  headlineLG: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 32,
    fontWeight: '700' as const,
    lineHeight: 38,
    letterSpacing: -0.32, // -0.01em
  },
  headlineMD: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 24,
    fontWeight: '700' as const,
    lineHeight: 30,
    letterSpacing: 0,
  },
  titleLG: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 22,
    fontWeight: '700' as const,
    lineHeight: 28,
    letterSpacing: 0,
  },
  titleMD: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 16,
    fontWeight: '700' as const,
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  titleSM: {
    fontFamily: 'Plus Jakarta Sans',
    fontSize: 14,
    fontWeight: '700' as const,
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  bodyLG: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 18,
    fontWeight: '400' as const,
    lineHeight: 28,
    letterSpacing: 0.5,
  },
  bodyMD: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
    letterSpacing: 0.25,
  },
  bodySM: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  labelLG: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 14,
    fontWeight: '600' as const,
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  labelMD: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 12,
    fontWeight: '600' as const,
    lineHeight: 16,
    letterSpacing: 0.5,
  },
  labelSM: {
    fontFamily: 'Be Vietnam Pro',
    fontSize: 11,
    fontWeight: '500' as const,
    lineHeight: 16,
    letterSpacing: 0.5,
  },
};

// ==================== SPACING ====================
export const Spacing = {
  xs: 4,      // Extra pequeño
  sm: 8,      // Pequeño (base)
  md: 12,     // Medio
  lg: 16,     // Grande
  xl: 24,     // Extra grande
  xxl: 32,    // Extra extra grande
  full: 9999, // Para border-radius circular
};

// ==================== BORDER RADIUS ====================
export const BorderRadius = {
  xs: 2,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  full: 9999,
};

// ==================== SHADOWS ====================
export const Shadows = {
  sm: {
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  md: {
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
  },
  lg: {
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 16,
  },
  xl: {
    elevation: 12,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 12 },
    shadowRadius: 24,
  },
};

// ==================== BREAKPOINTS (para web) ====================
export const Breakpoints = {
  sm: 360,   // Mobile
  md: 600,   // Tablet
  lg: 1024,  // Desktop
  xl: 1440,  // Large desktop
};