import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { colors } from '../../constants/colors';
import AstroButton from '../../components/ui/AstroButton';
import { registerWithEmail } from '../../services/firebase/auth';

export default function RegisterScreen() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleRegister() {
    if (!name || !email || !password) {
      Alert.alert('Hata', 'Tüm alanları doldurun.');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Hata', 'Şifre en az 6 karakter olmalı.');
      return;
    }
    setLoading(true);
    try {
      await registerWithEmail(email.trim(), password, name.trim());
      router.replace('/(tabs)');
    } catch (err: any) {
      const msg = err.code === 'auth/email-already-in-use'
        ? 'Bu e-posta zaten kayıtlı.'
        : 'Kayıt oluşturulamadı. Lütfen tekrar deneyin.';
      Alert.alert('Kayıt Hatası', msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <LinearGradient colors={['#0A0A0F', '#1A0A2E', '#0A0A0F']} style={styles.gradient}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
          <View style={styles.logoContainer}>
            <Text style={styles.logoSymbol}>✦</Text>
            <Text style={styles.logoText}>Hesap Oluştur</Text>
            <Text style={styles.logoSub}>Astrolura AI'ya katıl</Text>
          </View>

          <View style={styles.form}>
            <Text style={styles.label}>Ad Soyad</Text>
            <TextInput
              style={styles.input}
              placeholder="Adınız Soyadınız"
              placeholderTextColor={colors.textMuted}
              value={name}
              onChangeText={setName}
            />

            <Text style={styles.label}>E-posta</Text>
            <TextInput
              style={styles.input}
              placeholder="ornek@mail.com"
              placeholderTextColor={colors.textMuted}
              keyboardType="email-address"
              autoCapitalize="none"
              value={email}
              onChangeText={setEmail}
            />

            <Text style={styles.label}>Şifre</Text>
            <TextInput
              style={styles.input}
              placeholder="En az 6 karakter"
              placeholderTextColor={colors.textMuted}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />

            <AstroButton
              title="Kayıt Ol"
              onPress={handleRegister}
              loading={loading}
              style={styles.btn}
            />

            <TouchableOpacity
              onPress={() => router.back()}
              style={styles.loginLink}
            >
              <Text style={styles.loginText}>
                Zaten hesabın var mı?{' '}
                <Text style={styles.loginTextBold}>Giriş Yap</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  gradient: { flex: 1 },
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 28,
    paddingVertical: 48,
  },
  logoContainer: { alignItems: 'center', marginBottom: 40 },
  logoSymbol: { fontSize: 48, color: colors.accent, marginBottom: 8 },
  logoText: { fontSize: 28, fontWeight: '700', color: colors.text },
  logoSub: { fontSize: 14, color: colors.textSecondary, marginTop: 4 },
  form: { gap: 8 },
  label: { color: colors.textSecondary, fontSize: 13, marginBottom: 4, marginTop: 8 },
  input: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    color: colors.text,
    fontSize: 15,
  },
  btn: { marginTop: 24 },
  loginLink: { alignItems: 'center', marginTop: 16 },
  loginText: { color: colors.textSecondary, fontSize: 14 },
  loginTextBold: { color: colors.primary, fontWeight: '600' },
});
