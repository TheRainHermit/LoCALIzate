import { TouchableOpacity, Text, type TouchableOpacityProps, ActivityIndicator } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '@/constants/designTokens';

export type ButtonProps = TouchableOpacityProps & {
  variant?: 'filled' | 'outlined' | 'tonal' | 'text';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
  label: string;
  icon?: React.ReactNode;
};

export function Button({
  variant = 'filled',
  size = 'md',
  isLoading = false,
  disabled = false,
  label,
  icon,
  style,
  onPress,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || isLoading;

  // Determine sizes
  const sizes = {
    sm: { paddingHorizontal: Spacing.md, paddingVertical: Spacing.xs, fontSize: 12 },
    md: { paddingHorizontal: Spacing.lg, paddingVertical: Spacing.sm, fontSize: 14 },
    lg: { paddingHorizontal: Spacing.xl, paddingVertical: Spacing.md, fontSize: 16 },
  };

  // Determine styles by variant
  const variants = {
    filled: {
      backgroundColor: isDisabled ? Colors.surfaceContainerHigh : Colors.primary,
      borderWidth: 0,
    },
    outlined: {
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: isDisabled ? Colors.outline : Colors.outline,
    },
    tonal: {
      backgroundColor: isDisabled ? Colors.surfaceContainerHigh : Colors.primaryContainer,
      borderWidth: 0,
    },
    text: {
      backgroundColor: 'transparent',
      borderWidth: 0,
    },
  };

  const textColors = {
    filled: isDisabled ? Colors.onSurfaceVariant : Colors.onPrimary,
    outlined: isDisabled ? Colors.onSurfaceVariant : Colors.primary,
    tonal: isDisabled ? Colors.onSurfaceVariant : Colors.onPrimaryContainer,
    text: isDisabled ? Colors.onSurfaceVariant : Colors.primary,
  };

  return (
    <TouchableOpacity
      {...rest}
      disabled={isDisabled}
      onPress={onPress}
      activeOpacity={0.7}
      style={[
        {
          paddingHorizontal: sizes[size].paddingHorizontal,
          paddingVertical: sizes[size].paddingVertical,
          borderRadius: BorderRadius.lg,
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: Spacing.sm,
          ...variants[variant],
        },
        style,
      ]}
    >
      {isLoading ? (
        <ActivityIndicator color={textColors[variant]} size="small" />
      ) : (
        icon
      )}
      <Text
        style={{
          ...Typography.labelLG,
          color: textColors[variant],
          fontSize: sizes[size].fontSize,
        }}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );
}