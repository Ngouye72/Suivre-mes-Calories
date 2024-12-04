import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, List, Chip, ProgressBar, Colors } from 'react-native-paper';
import { LineChart, PieChart } from 'react-native-chart-kit';
import { getDetailedHabitsAnalysis } from '../services/api';

const EatingHabitsScreen = () => {
  const [analysis, setAnalysis] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAnalysis();
  }, [selectedPeriod]);

  const loadAnalysis = async () => {
    try {
      const data = await getDetailedHabitsAnalysis(selectedPeriod);
      setAnalysis(data);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'analyse:', error);
    }
  };

  const renderMealTimingSection = () => {
    if (!analysis?.meal_timing) return null;

    const mealTimes = analysis.meal_timing.meal_time_distribution;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Horaires des repas</Title>
          
          {Object.entries(mealTimes).map(([meal, data]) => (
            <View key={meal} style={styles.mealTimeItem}>
              <Title style={styles.mealTitle}>
                {meal.charAt(0).toUpperCase() + meal.slice(1)}
              </Title>
              <Paragraph>Heure moyenne: {Math.round(data.average_time)}h</Paragraph>
              <Paragraph>
                Régularité: {data.consistency < 1 ? 'Excellente' : data.consistency < 2 ? 'Bonne' : 'À améliorer'}
              </Paragraph>
              <ProgressBar
                progress={1 - (data.consistency / 4)}
                color={Colors.blue500}
                style={styles.progressBar}
              />
            </View>
          ))}

          {analysis.meal_timing.late_night_eating > 0 && (
            <Chip icon="alert" style={styles.warningChip}>
              {analysis.meal_timing.late_night_eating} repas tardifs détectés
            </Chip>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderPortionControlSection = () => {
    if (!analysis?.portion_control) return null;

    const { meal_size_consistency, daily_calorie_consistency } = analysis.portion_control;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Contrôle des portions</Title>

          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Title>{Math.round(daily_calorie_consistency.average_daily_calories)}</Title>
              <Paragraph>Calories/jour</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Title>{daily_calorie_consistency.days_over_target}</Title>
              <Paragraph>Jours > objectif</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Title>{daily_calorie_consistency.days_under_target}</Title>
              <Paragraph>Jours < objectif</Paragraph>
            </View>
          </View>

          <Title style={styles.subtitle}>Taille des repas</Title>
          {Object.entries(meal_size_consistency).map(([meal, data]) => (
            <View key={meal} style={styles.mealSizeItem}>
              <Paragraph>
                {meal}: {Math.round(data.average_size)} kcal 
                (±{Math.round(data.variation)} kcal)
              </Paragraph>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderEatingPatternsSection = () => {
    if (!analysis?.eating_patterns) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Schémas alimentaires</Title>

          <Title style={styles.subtitle}>Fréquence des repas</Title>
          {Object.entries(analysis.eating_patterns.meal_frequency).map(([meal, frequency]) => (
            <View key={meal} style={styles.frequencyItem}>
              <Paragraph>{meal}</Paragraph>
              <ProgressBar
                progress={frequency / selectedPeriod}
                color={Colors.blue500}
                style={styles.progressBar}
              />
              <Paragraph>{Math.round(frequency / selectedPeriod * 100)}%</Paragraph>
            </View>
          ))}

          <Title style={styles.subtitle}>Repas sautés</Title>
          {Object.entries(analysis.eating_patterns.skipped_meals).map(([meal, count]) => (
            <Chip key={meal} style={styles.chip}>
              {meal}: {count} fois
            </Chip>
          ))}

          <Title style={styles.subtitle}>Grignotage</Title>
          {Object.entries(analysis.eating_patterns.snacking_patterns).map(([period, count]) => (
            <View key={period} style={styles.snackingItem}>
              <Paragraph>{period}</Paragraph>
              <ProgressBar
                progress={count / selectedPeriod}
                color={Colors.orange500}
                style={styles.progressBar}
              />
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderFoodVarietySection = () => {
    if (!analysis?.food_variety) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Variété alimentaire</Title>

          <View style={styles.varietyStats}>
            <Title style={styles.subtitle}>Score de variété quotidien</Title>
            <Paragraph>
              Moyenne: {Math.round(analysis.food_variety.daily_variety.average_unique_foods)} aliments différents
            </Paragraph>
            <ProgressBar
              progress={analysis.food_variety.daily_variety.average_unique_foods / 15}
              color={Colors.green500}
              style={styles.progressBar}
            />
          </View>

          <Title style={styles.subtitle}>Aliments les plus fréquents</Title>
          {Object.entries(analysis.food_variety.most_repeated_foods).map(([food, count]) => (
            <Chip key={food} style={styles.chip}>
              {food}: {count} fois
            </Chip>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderImprovementAreas = () => {
    if (!analysis?.improvement_areas) return null;

    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>Domaines d'amélioration</Title>
          {analysis.improvement_areas.map((improvement, index) => (
            <List.Item
              key={index}
              title={improvement.description}
              description={improvement.recommendation}
              left={props => <List.Icon {...props} icon="alert" />}
              titleStyle={styles.improvementTitle}
            />
          ))}
        </Card.Content>
      </Card>
    );
  };

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

      {renderMealTimingSection()}
      {renderPortionControlSection()}
      {renderEatingPatternsSection()}
      {renderFoodVarietySection()}
      {renderImprovementAreas()}
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
  mealTimeItem: {
    marginVertical: 8,
  },
  mealTitle: {
    fontSize: 16,
  },
  progressBar: {
    marginVertical: 4,
    height: 8,
    borderRadius: 4,
  },
  warningChip: {
    marginTop: 8,
    backgroundColor: Colors.orange100,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 8,
  },
  mealSizeItem: {
    marginVertical: 4,
  },
  frequencyItem: {
    marginVertical: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  snackingItem: {
    marginVertical: 4,
  },
  varietyStats: {
    marginVertical: 8,
  },
  improvementTitle: {
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default EatingHabitsScreen;
