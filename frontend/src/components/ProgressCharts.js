import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { Card, Title } from 'react-native-paper';
import { LineChart, PieChart } from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

const ProgressCharts = ({ weeklyStats, monthlyProgress, nutritionDistribution }) => {
  const prepareWeeklyData = () => {
    const dates = Object.keys(weeklyStats).sort();
    return {
      labels: dates.map(date => date.slice(5)), // Format MM-DD
      datasets: [{
        data: dates.map(date => weeklyStats[date].calories)
      }]
    };
  };

  const prepareWeightData = () => {
    const data = monthlyProgress.weight_progress;
    return {
      labels: data.map(entry => entry.date.slice(5)),
      datasets: [{
        data: data.map(entry => entry.weight)
      }]
    };
  };

  const prepareMealDistribution = () => {
    const colors = {
      'petit-dejeuner': '#FF6384',
      'dejeuner': '#36A2EB',
      'diner': '#FFCE56',
      'collation': '#4BC0C0'
    };

    return nutritionDistribution.map(meal => ({
      name: meal.meal_type,
      calories: meal.calories,
      color: colors[meal.meal_type] || '#FF6384',
      legendFontColor: '#7F7F7F',
      legendFontSize: 12
    }));
  };

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(98, 0, 238, ${opacity})`,
    style: {
      borderRadius: 16
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Calories hebdomadaires</Title>
          <LineChart
            data={prepareWeeklyData()}
            width={screenWidth - 40}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Progression du poids</Title>
          <LineChart
            data={prepareWeightData()}
            width={screenWidth - 40}
            height={220}
            chartConfig={{
              ...chartConfig,
              color: (opacity = 1) => `rgba(0, 150, 136, ${opacity})`
            }}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Distribution des repas</Title>
          <PieChart
            data={prepareMealDistribution()}
            width={screenWidth - 40}
            height={220}
            chartConfig={chartConfig}
            accessor="calories"
            backgroundColor="transparent"
            paddingLeft="15"
            absolute
          />
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
  card: {
    marginBottom: 20,
    elevation: 4,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});

export default ProgressCharts;
