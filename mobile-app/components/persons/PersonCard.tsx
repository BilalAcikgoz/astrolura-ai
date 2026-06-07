import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../constants/colors';
import { Person } from '../../types/person.types';

interface Props {
  person: Person;
  onPress: () => void;
  onDelete?: () => void;
}

export default function PersonCard({ person, onPress, onDelete }: Props) {
  function confirmDelete() {
    Alert.alert('Sil', `${person.name} kişisini silmek istiyor musun?`, [
      { text: 'İptal', style: 'cancel' },
      { text: 'Sil', style: 'destructive', onPress: onDelete },
    ]);
  }

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.75}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{person.name[0].toUpperCase()}</Text>
      </View>
      {/* Yalnızca isim — detaylar harita sayfasının üstünde gösterilecek */}
      <Text style={styles.name}>{person.name}</Text>
      <View style={styles.actions}>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
        {onDelete && (
          <TouchableOpacity onPress={confirmDelete} style={styles.deleteBtn}>
            <Ionicons name="trash-outline" size={16} color={colors.error} />
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    gap: 12,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primary + '33',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { fontSize: 18, fontWeight: '700', color: colors.primary },
  name: { flex: 1, fontSize: 16, fontWeight: '600', color: colors.text },
  actions: { alignItems: 'center', gap: 8 },
  deleteBtn: { padding: 4 },
});
