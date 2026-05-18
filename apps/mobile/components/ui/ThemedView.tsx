import { View, type ViewProps } from 'react-native';
import { Colors, Spacing, BorderRadius } from '@/constants/designTokens';

export type ThemedViewProps = ViewProps & {
  variant?: 'surface' | 'container' | 'containerLow' | 'containerHigh';
  padding?: keyof typeof Spacing;
  margin?: keyof typeof Spacing;
  gap?: keyof typeof Spacing;
  rounded?: keyof typeof BorderRadius;
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
};

export function ThemedView({
  variant = 'surface',
  padding,
  margin,
  gap,
  rounded = 'md',
  shadow = 'none',
  style,
  ...rest
}: ThemedViewProps) {
  const bgColor =
    variant === 'surface'
      ? Colors.surface
      : variant === 'container'
        ? Colors.surfaceContainer
        : variant === 'containerLow'
          ? Colors.surfaceContainerLow
          : Colors.surfaceContainerHigh;

  return (
    <View
      {...rest}
      style={[
        {
          backgroundColor: bgColor,
          paddingHorizontal: padding ? Spacing[padding] : 0,
          paddingVertical: padding ? Spacing[padding] : 0,
          marginHorizontal: margin ? Spacing[margin] : 0,
          marginVertical: margin ? Spacing[margin] : 0,
          gap: gap ? Spacing[gap] : 0,
          borderRadius: BorderRadius[rounded],
        },
        shadow !== 'none' && {
          shadowColor: '#000',
          shadowOpacity: shadow === 'sm' ? 0.08 : shadow === 'md' ? 0.1 : shadow === 'lg' ? 0.12 : 0.15,
          shadowRadius: shadow === 'sm' ? 4 : shadow === 'md' ? 8 : shadow === 'lg' ? 16 : 24,
          elevation: shadow === 'sm' ? 2 : shadow === 'md' ? 4 : shadow === 'lg' ? 8 : 12,
        },
        style,
      ]}
    />
  );
}