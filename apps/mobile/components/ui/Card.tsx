import { View, type ViewProps } from 'react-native';
import { Colors, BorderRadius, Spacing } from '@/constants/designTokens';

export type CardProps = ViewProps & {
  variant?: 'elevated' | 'filled' | 'outlined';
};

export function Card({
  variant = 'elevated',
  style,
  ...rest
}: CardProps) {
  const variants = {
    elevated: {
      backgroundColor: Colors.surface,
      borderWidth: 0,
      shadowColor: '#000',
      shadowOpacity: 0.1,
      shadowOffset: { width: 0, height: 4 },
      shadowRadius: 8,
      elevation: 4,
    },
    filled: {
      backgroundColor: Colors.surfaceContainer,
      borderWidth: 0,
    },
    outlined: {
      backgroundColor: Colors.surface,
      borderWidth: 1,
      borderColor: Colors.outline,
    },
  };

  return (
    <View
      {...rest}
      style={[
        {
          borderRadius: BorderRadius.lg,
          padding: Spacing.lg,
          ...variants[variant],
        },
        style,
      ]}
    />
  );
}