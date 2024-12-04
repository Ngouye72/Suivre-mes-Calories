import React, { useState, useEffect } from 'react';
import { ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';
import ProgressCharts from '../components/ProgressCharts';
import NutritionCard from '../components/NutritionCard';
import { getDailyStats, getWeeklyStats, getMonthlyProgress, getNutritionDistribution } from '../services/api';

const StatsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    daily: null,
    weekly: null,
    monthly: null,
    distribution: null,
  });

  const loadStats = async () => {
    try {
      const [daily, weekly, monthly, distribution] = await Promise.all([
        getDailyStats(),
        getWeeklyStats(),
        getMonthlyProgress(),
        getNutritionDistribution(),
      ]);

      setStats({
        daily,
        weekly,
        monthly,
        distribution,
      });
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadStats();
  };

  if (loading) {
    return (
      <ActivityIndicator
        style={styles.loading}
        size="large"
      />
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
        />
      }
    >
      {stats.daily && (
        <NutritionCard
          daily={stats.daily.daily}
          target={stats.daily.target}
        />
      )}

      {stats.weekly && stats.monthly && stats.distribution && (
        <ProgressCharts
          weeklyStats={stats.weekly}
          monthlyProgress={stats.monthly}
          nutritionDistribution={stats.distribution}
        />
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default StatsScreen;
