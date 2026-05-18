import { TouchableOpacity, type TouchableOpacityProps } from 'react-native';
import { Colors, BorderRadius } from '@/constants/designTokens';

export type IconButtonProps = TouchableOpacityProps & {
  icon: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'filled' | 'outlined' | 'tonal';
};

const sizes = {
  sm: 32,
  md: 44,
  lg: 56,
};

const variantStyles = {
  filled: {
    backgroundColor: Colors.primary,
  },
  outlined: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: Colors.outline,
  },
  tonal: {
    backgroundColor: Colors.primaryContainer,
  },
};

export function IconButton({
  icon,
  size = 'md',
  variant = 'filled',
  style,
  ...rest
}: IconButtonProps) {
  const dimension = sizes[size];

  return (
    <TouchableOpacity
      {...rest}
      style={[
        {
          width: dimension,
          height: dimension,
          borderRadius: BorderRadius.full,
          justifyContent: 'center',
          alignItems: 'center',
          ...variantStyles[variant],
        },
        style,
      ]}
      activeOpacity={0.7}
    >
      {icon}
    </TouchableOpacity>
  );
}