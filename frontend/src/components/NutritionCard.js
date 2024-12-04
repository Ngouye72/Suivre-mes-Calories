import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, ProgressBar } from 'react-native-paper';

const NutritionCard = ({ daily, target }) => {
  const calculateProgress = (current, max) => {
    return Math.min(current / max, 1);
  };

  const calculateRemaining = (current, max) => {
    return Math.max(max - current, 0);
  };

  return (
    <Card style={styles.container}>
      <Card.Content>
        <Title>Nutrition Journalière</Title>

        <View style={styles.nutrientContainer}>
          <Title style={styles.nutrientTitle}>Calories</Title>
          <Paragraph>{daily.calories} / {target.calories} kcal</Paragraph>
          <ProgressBar
            progress={calculateProgress(daily.calories, target.calories)}
            color="#6200ee"
            style={styles.progressBar}
          />
          <Paragraph style={styles.remaining}>
            Restant: {calculateRemaining(daily.calories, target.calories)} kcal
          </Paragraph>
        </View>

        <View style={styles.macrosContainer}>
          <View style={styles.nutrientContainer}>
            <Title style={styles.nutrientTitle}>Protéines</Title>
            <Paragraph>{daily.proteins} / {target.proteins}g</Paragraph>
            <ProgressBar
              progress={calculateProgress(daily.proteins, target.proteins)}
              color="#00796B"
              style={styles.progressBar}
            />
          </View>

          <View style={styles.nutrientContainer}>
            <Title style={styles.nutrientTitle}>Glucides</Title>
            <Paragraph>{daily.carbs} / {target.carbs}g</Paragraph>
            <ProgressBar
              progress={calculateProgress(daily.carbs, target.carbs)}
              color="#FFA000"
              style={styles.progressBar}
            />
          </View>

          <View style={styles.nutrientContainer}>
            <Title style={styles.nutrientTitle}>Lipides</Title>
            <Paragraph>{daily.fats} / {target.fats}g</Paragraph>
            <ProgressBar
              progress={calculateProgress(daily.fats, target.fats)}
              color="#C62828"
              style={styles.progressBar}
            />
          </View>
        </View>
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: 16,
  },
  nutrientContainer: {
    marginVertical: 8,
  },
  nutrientTitle: {
    fontSize: 16,
    marginBottom: 4,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    marginVertical: 4,
  },
  remaining: {
    fontSize: 12,
    color: '#666',
  },
  macrosContainer: {
    marginTop: 16,
  },
});

export default NutritionCard;
