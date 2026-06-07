import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../constants/colors';
import { useAuth } from '../../context/AuthContext';
import { logout } from '../../services/firebase/auth';

const MODULES = [
  {
    id: 'birth-chart',
    title: 'Doğum Haritası',
    subtitle: 'Natal haritanı incele',
    icon: 'planet-outline',
    color: colors.primary,
    route: '/(tabs)/birth-chart',
  },
  {
    id: 'transit-chart',
    title: 'Transit Harita',
    subtitle: 'Güncel transit hareketleri',
    icon: 'globe-outline',
    color: colors.accent,
    route: '/(tabs)/transit-chart',
  },
];

function getTodayStr() {
  const d = new Date();
  return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default function HomeScreen() {
  const { user } = useAuth();
  const displayName = user?.displayName || user?.email?.split('@')[0] || 'Kullanıcı';

  async function handleLogout() {
    await logout();
  }

  return (
    <LinearGradient colors={['#0A0A0F', '#0E0818', '#0A0A0F']} style={styles.gradient}>
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <View style={styles.header}>
            <View>
              <Text style={styles.greeting}>Merhaba, {displayName} ✦</Text>
              <Text style={styles.date}>{getTodayStr()}</Text>
            </View>
            <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
              <Ionicons name="log-out-outline" size={22} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>

          {/* Hero Card */}
          <LinearGradient
            colors={[colors.card, '#1E0A3E']}
            style={styles.heroCard}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <Text style={styles.heroSymbol}>✦</Text>
            <Text style={styles.heroTitle}>Astrolura AI</Text>
            <Text style={styles.heroSub}>
              Natal haritandan kişiselleştirilmiş yıldız yorumlarına ulaş
            </Text>
          </LinearGradient>

          {/* Modules */}
          <Text style={styles.sectionTitle}>Modüller</Text>
          <View style={styles.moduleGrid}>
            {MODULES.map((mod) => (
              <TouchableOpacity
                key={mod.id}
                style={styles.moduleCard}
                onPress={() => router.push(mod.route as any)}
                activeOpacity={0.75}
              >
                <View style={[styles.moduleIcon, { backgroundColor: mod.color + '22' }]}>
                  <Ionicons name={mod.icon as any} size={32} color={mod.color} />
                </View>
                <Text style={styles.moduleTitle}>{mod.title}</Text>
                <Text style={styles.moduleSub}>{mod.subtitle}</Text>
                <Ionicons
                  name="chevron-forward"
                  size={16}
                  color={colors.textMuted}
                  style={styles.moduleArrow}
                />
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },
  container: { paddingHorizontal: 20, paddingTop: 16, paddingBottom: 32 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  greeting: { fontSize: 20, fontWeight: '700', color: colors.text },
  date: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  logoutBtn: { padding: 8 },
  heroCard: {
    borderRadius: 20,
    padding: 28,
    alignItems: 'center',
    marginBottom: 32,
    borderWidth: 1,
    borderColor: colors.primary + '44',
  },
  heroSymbol: { fontSize: 40, color: colors.accent, marginBottom: 8 },
  heroTitle: { fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 8 },
  heroSub: { fontSize: 13, color: colors.textSecondary, textAlign: 'center', lineHeight: 20 },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: 16,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  moduleGrid: { gap: 14 },
  moduleCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.cardBorder,
  },
  moduleIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  moduleTitle: { fontSize: 17, fontWeight: '700', color: colors.text, marginBottom: 4 },
  moduleSub: { fontSize: 13, color: colors.textSecondary },
  moduleArrow: { position: 'absolute', right: 20, top: '50%' },
});
