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
import GoogleSignInButton from '../../components/auth/SocialSignIn';
import { loginWithEmail } from '../../services/firebase/auth';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    if (!email || !password) {
      Alert.alert('Hata', 'E-posta ve şifre gerekli.');
      return;
    }
    setLoading(true);
    try {
      await loginWithEmail(email.trim(), password);
      router.replace('/(tabs)');
    } catch (err: any) {
      const msg = err.code === 'auth/invalid-credential'
        ? 'E-posta veya şifre hatalı.'
        : 'Giriş yapılamadı. Lütfen tekrar deneyin.';
      Alert.alert('Giriş Hatası', msg);
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
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Text style={styles.logoSymbol}>✦</Text>
            <Text style={styles.logoText}>Astrolura AI</Text>
            <Text style={styles.logoSub}>Haritanı keşfet</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
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
              placeholder="••••••••"
              placeholderTextColor={colors.textMuted}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />

            <AstroButton
              title="Giriş Yap"
              onPress={handleLogin}
              loading={loading}
              style={styles.loginBtn}
            />

            {/* Divider */}
            <View style={styles.divider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>veya</Text>
              <View style={styles.dividerLine} />
            </View>

            <GoogleSignInButton
              onSuccess={() => router.replace('/(tabs)')}
              onError={(msg) => Alert.alert('Giriş Hatası', msg)}
            />

            <TouchableOpacity
              onPress={() => router.push('/(auth)/register')}
              style={styles.registerLink}
            >
              <Text style={styles.registerText}>
                Hesabın yok mu?{' '}
                <Text style={styles.registerTextBold}>Kayıt Ol</Text>
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
  logoContainer: { alignItems: 'center', marginBottom: 48 },
  logoSymbol: { fontSize: 56, color: colors.accent, marginBottom: 8 },
  logoText: { fontSize: 32, fontWeight: '700', color: colors.text, letterSpacing: 1 },
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
  loginBtn: { marginTop: 24 },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
    gap: 12,
  },
  dividerLine: { flex: 1, height: 1, backgroundColor: colors.cardBorder },
  dividerText: { color: colors.textSecondary, fontSize: 13 },
  registerLink: { alignItems: 'center', marginTop: 16 },
  registerText: { color: colors.textSecondary, fontSize: 14 },
  registerTextBold: { color: colors.primary, fontWeight: '600' },
});
