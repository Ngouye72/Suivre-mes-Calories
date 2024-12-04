import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, ProgressBar, List, Chip, Colors } from 'react-native-paper';
import { LineChart, PieChart } from 'react-native-chart-kit';
import { getDetailedNutritionAnalysis, getMealSuggestions } from '../services/api';

const NutritionAnalysisScreen = () => {
  const [analysis, setAnalysis] = useState(null);
  const [mealSuggestions, setMealSuggestions] = useState({});
  const [selectedPeriod, setSelectedPeriod] = useState(7);

  useEffect(() => {
    loadAnalysis();
  }, [selectedPeriod]);

  const loadAnalysis = async () => {
    try {
      const data = await getDetailedNutritionAnalysis(selectedPeriod);
      setAnalysis(data);

      const suggestions = await getMealSuggestions();
      setMealSuggestions(suggestions);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'analyse:', error);
    }
  };

  const renderCaloriesTrend = () => {
    if (!analysis?.calories?.trend) return null;

    const data = {
      labels: Array.from({ length: selectedPeriod }, (_, i) => `J${i + 1}`),
      datasets: [{
        data: analysis.calories.trend.values
      }]
    };

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Tendance des calories</Title>
          <LineChart
            data={data}
            width={350}
            height={200}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
            }}
            bezier
            style={styles.chart}
          />
          <Paragraph style={styles.trendInfo}>
            Tendance : {analysis.calories.trend.direction}
            {analysis.calories.trend.slope > 10 && ' (changement significatif)'}
          </Paragraph>
        </Card.Content>
      </Card>
    );
  };

  const renderMacronutrients = () => {
    if (!analysis?.macronutrients) return null;

    const data = [
      {
        name: 'Protéines',
        percentage: analysis.macronutrients.proteins.percentage,
        color: '#FF6B6B'
      },
      {
        name: 'Glucides',
        percentage: analysis.macronutrients.carbs.percentage,
        color: '#4ECDC4'
      },
      {
        name: 'Lipides',
        percentage: analysis.macronutrients.fats.percentage,
        color: '#45B7D1'
      }
    ];

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Répartition des macronutriments</Title>
          <PieChart
            data={data}
            width={350}
            height={200}
            chartConfig={{
              color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            }}
            accessor="percentage"
            backgroundColor="transparent"
            paddingLeft="15"
          />
          {data.map((item, index) => (
            <View key={index} style={styles.macroItem}>
              <View style={[styles.colorDot, { backgroundColor: item.color }]} />
              <Paragraph>{item.name}: {Math.round(item.percentage)}%</Paragraph>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderMealPatterns = () => {
    if (!analysis?.meal_patterns) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Habitudes alimentaires</Title>
          {Object.entries(analysis.meal_patterns).map(([meal, stats]) => (
            <View key={meal} style={styles.mealPattern}>
              <Title style={styles.mealTitle}>
                {meal.charAt(0).toUpperCase() + meal.slice(1)}
              </Title>
              <Paragraph>Fréquence: {stats.frequency} fois</Paragraph>
              <Paragraph>Calories moyennes: {Math.round(stats.average_calories)} kcal</Paragraph>
              <ProgressBar
                progress={stats.frequency / selectedPeriod}
                color={Colors.blue500}
                style={styles.progressBar}
              />
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderRecommendations = () => {
    if (!analysis?.recommendations) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Recommandations personnalisées</Title>
          {analysis.recommendations.map((rec, index) => (
            <List.Item
              key={index}
              title={rec.title}
              description={rec.description}
              left={props => <List.Icon {...props} icon="lightbulb" />}
              titleStyle={styles.recommendationTitle}
            />
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderMealSuggestions = () => {
    if (!mealSuggestions) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Suggestions de repas</Title>
          {Object.entries(mealSuggestions).map(([mealType, suggestions]) => (
            <View key={mealType}>
              <Title style={styles.mealType}>
                {mealType.charAt(0).toUpperCase() + mealType.slice(1)}
              </Title>
              {suggestions.map((meal, index) => (
                <Card style={styles.mealCard} key={index}>
                  <Card.Content>
                    <Title style={styles.mealName}>{meal.name}</Title>
                    <View style={styles.nutritionInfo}>
                      <Chip icon="fire">{meal.calories} kcal</Chip>
                      <Chip icon="protein">P: {meal.proteins}g</Chip>
                      <Chip icon="carbohydrates">G: {meal.carbs}g</Chip>
                      <Chip icon="oil">L: {meal.fats}g</Chip>
                    </View>
                    <Paragraph style={styles.ingredients}>
                      {meal.ingredients.join(', ')}
                    </Paragraph>
                    <Paragraph>Temps de préparation: {meal.preparation_time} min</Paragraph>
                  </Card.Content>
                </Card>
              ))}
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  if (!analysis) {
    return null;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.periodSelector}>
        {[7, 14, 30].map(period => (
          <Chip
            key={period}
            selected={selectedPeriod === period}
            onPress={() => setSelectedPeriod(period)}
            style={styles.periodChip}
          >
            {period} jours
          </Chip>
        ))}
      </View>

      {renderCaloriesTrend()}
      {renderMacronutrients()}
      {renderMealPatterns()}
      {renderRecommendations()}
      {renderMealSuggestions()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  periodSelector: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'white',
  },
  periodChip: {
    marginRight: 8,
  },
  card: {
    margin: 16,
    marginTop: 8,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  trendInfo: {
    marginTop: 8,
    fontStyle: 'italic',
  },
  macroItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  colorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  mealPattern: {
    marginVertical: 8,
  },
  mealTitle: {
    fontSize: 16,
  },
  progressBar: {
    marginTop: 4,
    height: 8,
    borderRadius: 4,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  mealType: {
    fontSize: 18,
    marginTop: 16,
    marginBottom: 8,
  },
  mealCard: {
    marginVertical: 8,
  },
  mealName: {
    fontSize: 16,
  },
  nutritionInfo: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginVertical: 8,
    gap: 8,
  },
  ingredients: {
    marginVertical: 8,
    fontStyle: 'italic',
  },
});

export default NutritionAnalysisScreen;
