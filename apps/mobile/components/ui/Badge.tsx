import { View, Text, type ViewProps } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '@/constants/designTokens';

export type BadgeProps = ViewProps & {
  label: string;
  color?: 'primary' | 'secondary' | 'tertiary' | 'error';
  size?: 'sm' | 'md';
};

export function Badge({
  label,
  color = 'primary',
  size = 'md',
  style,
  ...rest
}: BadgeProps) {
  const colors = {
    primary: { bg: Colors.primaryContainer, text: Colors.onPrimaryContainer },
    secondary: { bg: Colors.secondaryContainer, text: Colors.onSecondaryContainer },
    tertiary: { bg: Colors.tertiaryContainer, text: Colors.onTertiaryContainer },
    error: { bg: Colors.errorContainer, text: Colors.onErrorContainer },
  };

  const sizes = {
    sm: { padding: Spacing.xs, fontSize: 11 },
    md: { padding: Spacing.sm, fontSize: 12 },
  };

  return (
    <View
      {...rest}
      style={[
        {
          backgroundColor: colors[color].bg,
          borderRadius: BorderRadius.full,
          paddingHorizontal: sizes[size].padding * 1.5,
          paddingVertical: sizes[size].padding,
          alignSelf: 'flex-start',
        },
        style,
      ]}
    >
      <Text
        style={{
          ...Typography.labelSM,
          fontSize: sizes[size].fontSize,
          color: colors[color].text,
        }}
      >
        {label}
      </Text>
    </View>
  );
}