import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View, ActivityIndicator } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import * as AuthSession from 'expo-auth-session/providers/google';
import { colors } from '../../constants/colors';
import { signInWithGoogleCredential } from '../../services/firebase/auth';

WebBrowser.maybeCompleteAuthSession();

interface Props {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function GoogleSignInButton({ onSuccess, onError }: Props) {
  const [request, response, promptAsync] = AuthSession.useAuthRequest({
    webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID,
  });

  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (response?.type === 'success') {
      const { id_token } = response.params;
      if (id_token) {
        setLoading(true);
        signInWithGoogleCredential(id_token)
          .then(() => onSuccess?.())
          .catch(() => onError?.('Google ile giriş yapılamadı.'))
          .finally(() => setLoading(false));
      }
    } else if (response?.type === 'error') {
      onError?.('Google ile giriş yapılamadı.');
    }
  }, [response]);

  async function handlePress() {
    setLoading(true);
    try {
      await promptAsync();
    } finally {
      setLoading(false);
    }
  }

  return (
    <TouchableOpacity
      style={styles.button}
      onPress={handlePress}
      disabled={!request || loading}
      activeOpacity={0.85}
    >
      {loading ? (
        <ActivityIndicator color={colors.text} size="small" />
      ) : (
        <>
          <Text style={styles.googleLogo}>G</Text>
          <Text style={styles.label}>Google ile Giriş Yap</Text>
        </>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 20,
    gap: 10,
  },
  googleLogo: {
    fontSize: 18,
    fontWeight: '700',
    color: '#4285F4',
  },
  label: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F1F1F',
  },
});
