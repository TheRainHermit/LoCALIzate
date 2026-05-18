import { Text, type TextProps } from 'react-native';
import { Colors, Typography } from '@/constants/designTokens';

export type ThemedTextProps = TextProps & {
  variant?:
    | 'headlineXL'
    | 'headlineLG'
    | 'headlineMD'
    | 'titleLG'
    | 'titleMD'
    | 'titleSM'
    | 'bodyLG'
    | 'bodyMD'
    | 'bodySM'
    | 'labelLG'
    | 'labelMD'
    | 'labelSM';
  color?: keyof typeof Colors;
  bold?: boolean;
  center?: boolean;
};

export function ThemedText({
  variant = 'bodyMD',
  color = 'onBackground',
  bold = false,
  center = false,
  style,
  ...rest
}: ThemedTextProps) {
  const typographyStyle = Typography[variant];
  const textColor = Colors[color];

  return (
    <Text
      {...rest}
      style={[
        typographyStyle,
        {
          color: textColor,
          fontWeight: bold ? '700' : typographyStyle.fontWeight,
          textAlign: center ? 'center' : 'auto',
        },
        style,
      ]}
    />
  );
}