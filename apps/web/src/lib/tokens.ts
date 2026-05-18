/**
 * Design System Tokens - TypeScript
 * Para usar en componentes Astro con dynamic styles
 */

export const colors = {
  primary: '#7e5700',
  onPrimary: '#ffffff',
  primaryContainer: '#ffb300',
  onPrimaryContainer: '#6b4900',
  inversePrimary: '#ffba38',

  secondary: '#bb0020',
  onSecondary: '#ffffff',
  secondaryContainer: '#e12634',
  onSecondaryContainer: '#fffbff',

  tertiary: '#2c694e',
  onTertiary: '#ffffff',
  tertiaryContainer: '#90cfae',
  onTertiaryContainer: '#1a5a40',

  surface: '#fff8f3',
  surfaceContainer: '#faecdb',
  surfaceContainerLow: '#fff2e2',
  surfaceContainerHigh: '#f4e6d6',
  surfaceContainerHighest: '#eee0d0',
  onSurface: '#211b11',
  onSurfaceVariant: '#514532',
  surfaceVariant: '#eee0d0',

  background: '#fff8f3',
  onBackground: '#211b11',

  outline: '#847560',
  outlineVariant: '#d6c4ac',
  inverseSurface: '#372f24',
  inverseOnSurface: '#fdefde',

  error: '#ba1a1a',
  onError: '#ffffff',
  errorContainer: '#ffdad6',
  onErrorContainer: '#93000a',
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
} as const;

export const borderRadius = {
  xs: '2px',
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  xxl: '24px',
  full: '9999px',
} as const;

export const shadows = {
  sm: '0 2px 4px rgba(0, 0, 0, 0.08)',
  md: '0 4px 8px rgba(0, 0, 0, 0.1)',
  lg: '0 8px 16px rgba(0, 0, 0, 0.12)',
  xl: '0 12px 24px rgba(0, 0, 0, 0.15)',
} as const;

export const transitions = {
  fast: '150ms ease-in-out',
  normal: '300ms ease-in-out',
  slow: '500ms ease-in-out',
} as const;