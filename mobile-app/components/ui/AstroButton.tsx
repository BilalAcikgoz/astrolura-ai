import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet, ViewStyle } from 'react-native';
import { colors } from '../../constants/colors';

interface Props {
  title: string;
  onPress: () => void;
  loading?: boolean;
  variant?: 'primary' | 'outline' | 'ghost';
  disabled?: boolean;
  style?: ViewStyle;
}

export default function AstroButton({ title, onPress, loading, variant = 'primary', disabled, style }: Props) {
  const isDisabled = disabled || loading;
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      style={[styles.base, styles[variant], isDisabled && styles.disabled, style]}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'primary' ? '#fff' : colors.primary} size="small" />
      ) : (
        <Text style={[styles.text, variant !== 'primary' && styles.textOutline]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: {
    backgroundColor: colors.primary,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: colors.primary,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  textOutline: {
    color: colors.primary,
  },
});
