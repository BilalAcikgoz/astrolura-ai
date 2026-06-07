import React from 'react';
import { Tabs } from 'expo-router';
import { colors } from '../../constants/colors';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        // Alt tab bar tamamen gizli — navigasyon her sayfanın kendi geri tuşuyla yapılır
        tabBarStyle: { display: 'none' },
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Ana Sayfa' }} />
      <Tabs.Screen name="birth-chart" options={{ title: 'Doğum Haritası' }} />
      <Tabs.Screen name="transit-chart" options={{ title: 'Transit Harita' }} />
    </Tabs>
  );
}
