import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, ProgressBar } from 'react-native-paper';
import { LineChart } from 'react-native-chart-kit';
import { getDailyCalories, getWeeklyProgress } from '../services/api';

const HomeScreen = () => {
  const [dailyStats, setDailyStats] = useState({
    consumed: 0,
    target: 2000,
    remaining: 2000,
  });

  const [weeklyData, setWeeklyData] = useState({
    labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
    datasets: [{
      data: [0, 0, 0, 0, 0, 0, 0]
    }]
  });

  useEffect(() => {
    // Charger les données quotidiennes et hebdomadaires
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const daily = await getDailyCalories();
      const weekly = await getWeeklyProgress();
      setDailyStats(daily);
      setWeeklyData(weekly);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Objectif journalier</Title>
          <Paragraph>{dailyStats.consumed} / {dailyStats.target} calories</Paragraph>
          <ProgressBar
            progress={dailyStats.consumed / dailyStats.target}
            color="#6200ee"
            style={styles.progressBar}
          />
          <Paragraph>Restant: {dailyStats.remaining} calories</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Progression hebdomadaire</Title>
          <LineChart
            data={weeklyData}
            width={300}
            height={200}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(98, 0, 238, ${opacity})`,
              style: {
                borderRadius: 16
              }
            }}
            style={styles.chart}
          />
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  progressBar: {
    height: 10,
    borderRadius: 5,
    marginVertical: 10,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});

export default HomeScreen;
