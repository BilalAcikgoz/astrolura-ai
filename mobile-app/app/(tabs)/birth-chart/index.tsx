import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { colors } from '../../../constants/colors';
import PersonCard from '../../../components/persons/PersonCard';
import LoadingSpinner from '../../../components/ui/LoadingSpinner';
import { usePersons } from '../../../hooks/usePersons';

export default function BirthChartPersonList() {
  const { persons, loading, removePerson } = usePersons();
  const [search, setSearch] = useState('');

  const filtered = persons.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <LinearGradient colors={['#0A0A0F', '#0E0818']} style={styles.gradient}>
      <SafeAreaView style={styles.safe}>
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
              <Ionicons name="chevron-back" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <Text style={styles.title}>Doğum Haritası</Text>
          <Text style={styles.subtitle}>Kişi seçin veya ekleyin</Text>
        </View>

        <View style={styles.searchWrap}>
          <Ionicons name="search" size={18} color={colors.textMuted} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Kişi ara..."
            placeholderTextColor={colors.textMuted}
            value={search}
            onChangeText={setSearch}
          />
        </View>

        {loading ? (
          <LoadingSpinner message="Kişiler yükleniyor..." />
        ) : (
          <FlatList
            data={filtered}
            keyExtractor={(p) => p.id}
            renderItem={({ item }) => (
              <PersonCard
                person={item}
                onPress={() => router.push(`/(tabs)/birth-chart/${item.id}`)}
                onDelete={() => removePerson(item.id)}
              />
            )}
            contentContainerStyle={styles.list}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={styles.emptyIcon}>✦</Text>
                <Text style={styles.emptyText}>Henüz kişi eklenmemiş</Text>
                <Text style={styles.emptySub}>Aşağıdaki butona basarak kişi ekleyebilirsin</Text>
              </View>
            }
          />
        )}

        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => router.push('/persons/add')}
          activeOpacity={0.85}
        >
          <Ionicons name="add" size={24} color="#fff" />
          <Text style={styles.addBtnText}>Kişi Ekle</Text>
        </TouchableOpacity>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },
  header: { paddingHorizontal: 20, paddingTop: 16, marginBottom: 16 },
  headerTop: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  backBtn: { marginRight: 8, padding: 4 },
  title: { fontSize: 22, fontWeight: '700', color: colors.text },
  subtitle: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 12,
    marginHorizontal: 20,
    marginBottom: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: colors.cardBorder,
  },
  searchIcon: { marginRight: 8 },
  searchInput: { flex: 1, color: colors.text, fontSize: 14, paddingVertical: 12 },
  list: { paddingHorizontal: 20, paddingBottom: 80 },
  empty: { alignItems: 'center', marginTop: 60, gap: 8 },
  emptyIcon: { fontSize: 40, color: colors.primary },
  emptyText: { fontSize: 16, fontWeight: '600', color: colors.text },
  emptySub: { fontSize: 13, color: colors.textSecondary, textAlign: 'center' },
  addBtn: {
    position: 'absolute',
    bottom: 16,
    left: 20,
    right: 20,
    backgroundColor: colors.primary,
    borderRadius: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  addBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});
