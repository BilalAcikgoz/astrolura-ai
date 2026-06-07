import React from 'react';
import { ScrollView, Text, View, StyleSheet } from 'react-native';
import { colors } from '../../constants/colors';

interface Props {
  content: string;
}

// Minimal markdown renderer — başlıklar, bold, italik, liste öğeleri
export default function MarkdownRenderer({ content }: Props) {
  const lines = content.split('\n');

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {lines.map((line, i) => {
        if (line.startsWith('### ')) {
          return <Text key={i} style={styles.h3}>{line.slice(4)}</Text>;
        }
        if (line.startsWith('## ')) {
          return <Text key={i} style={styles.h2}>{line.slice(3)}</Text>;
        }
        if (line.startsWith('# ')) {
          return <Text key={i} style={styles.h1}>{line.slice(2)}</Text>;
        }
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return (
            <View key={i} style={styles.listRow}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.listText}>{parseBoldItalic(line.slice(2))}</Text>
            </View>
          );
        }
        if (line.startsWith('---')) {
          return <View key={i} style={styles.divider} />;
        }
        if (line.trim() === '') {
          return <View key={i} style={styles.spacer} />;
        }
        return <Text key={i} style={styles.body}>{parseBoldItalic(line)}</Text>;
      })}
      <View style={{ height: 32 }} />
    </ScrollView>
  );
}

function parseBoldItalic(text: string): React.ReactNode {
  // Basit bold (**text**) işleme
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) => {
    if (p.startsWith('**') && p.endsWith('**')) {
      return <Text key={i} style={{ fontWeight: '700', color: colors.accent }}>{p.slice(2, -2)}</Text>;
    }
    return p;
  });
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  h1: { color: colors.accent, fontSize: 22, fontWeight: '700', marginTop: 16, marginBottom: 8 },
  h2: { color: colors.primaryLight, fontSize: 18, fontWeight: '700', marginTop: 14, marginBottom: 6 },
  h3: { color: colors.text, fontSize: 15, fontWeight: '600', marginTop: 10, marginBottom: 4 },
  body: { color: colors.text, fontSize: 14, lineHeight: 22 },
  listRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 4, paddingLeft: 4 },
  bullet: { color: colors.primary, fontSize: 16, marginRight: 8, lineHeight: 22 },
  listText: { color: colors.text, fontSize: 14, lineHeight: 22, flex: 1 },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: 12 },
  spacer: { height: 8 },
});
