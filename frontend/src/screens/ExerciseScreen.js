import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Button, ProgressBar, Chip, Colors } from 'react-native-paper';
import { getExerciseSuggestions, getWeeklyPlan } from '../services/api';

const ExerciseScreen = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [weeklyPlan, setWeeklyPlan] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);

  useEffect(() => {
    loadExerciseData();
  }, []);

  const loadExerciseData = async () => {
    try {
      const suggestionsData = await getExerciseSuggestions();
      const planData = await getWeeklyPlan();
      setSuggestions(suggestionsData);
      setWeeklyPlan(planData);
      
      // Sélectionner le jour actuel
      const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
      const today = days[new Date().getDay()];
      setSelectedDay(today);
    } catch (error) {
      console.error('Erreur lors du chargement des données d\'exercice:', error);
    }
  };

  const renderExerciseCard = (exercise) => (
    <Card style={styles.exerciseCard} key={exercise.activity}>
      <Card.Content>
        <Title>{exercise.activity.charAt(0).toUpperCase() + exercise.activity.slice(1)}</Title>
        <Paragraph>Durée: {exercise.duration} minutes</Paragraph>
        <Paragraph>Calories: {exercise.calories_burned} kcal</Paragraph>
        
        <View style={styles.tagsContainer}>
          <Chip style={styles.intensityChip}>
            {exercise.intensity}
          </Chip>
        </View>

        <Paragraph style={styles.description}>{exercise.description}</Paragraph>

        <Title style={styles.subtitle}>Bénéfices</Title>
        {exercise.benefits.map((benefit, index) => (
          <Paragraph key={index}>• {benefit}</Paragraph>
        ))}

        {exercise.equipment_needed.length > 0 && (
          <>
            <Title style={styles.subtitle}>Équipement nécessaire</Title>
            {exercise.equipment_needed.map((equipment, index) => (
              <Paragraph key={index}>• {equipment}</Paragraph>
            ))}
          </>
        )}
      </Card.Content>
      <Card.Actions>
        <Button mode="contained" onPress={() => {}}>
          Commencer
        </Button>
      </Card.Actions>
    </Card>
  );

  const renderDayPlan = (day) => {
    const plan = weeklyPlan.find(p => p.day === day);
    if (!plan) return null;

    return (
      <Card style={styles.dayCard}>
        <Card.Content>
          <Title>{plan.day}</Title>
          <Paragraph style={styles.focusText}>Focus: {plan.focus}</Paragraph>

          {plan.activities.map((activity, index) => (
            <View key={index} style={styles.activityItem}>
              <Title style={styles.activityName}>
                {activity.name.charAt(0).toUpperCase() + activity.name.slice(1)}
              </Title>
              <Paragraph>Durée: {activity.duration} min</Paragraph>
              <Paragraph>Intensité: {activity.intensity}</Paragraph>
              <Paragraph>Calories: {activity.calories_burned} kcal</Paragraph>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.sectionTitle}>Programme hebdomadaire</Title>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.daysScroll}>
        {weeklyPlan.map((day) => (
          <Chip
            key={day.day}
            selected={selectedDay === day.day}
            onPress={() => setSelectedDay(day.day)}
            style={styles.dayChip}
          >
            {day.day}
          </Chip>
        ))}
      </ScrollView>

      {selectedDay && renderDayPlan(selectedDay)}

      <Title style={styles.sectionTitle}>Exercices suggérés</Title>
      {suggestions.map(renderExerciseCard)}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 10,
  },
  sectionTitle: {
    marginVertical: 16,
    marginLeft: 8,
  },
  exerciseCard: {
    marginBottom: 16,
  },
  dayCard: {
    marginBottom: 16,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginVertical: 8,
  },
  intensityChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  description: {
    marginVertical: 8,
  },
  subtitle: {
    fontSize: 16,
    marginTop: 12,
    marginBottom: 4,
  },
  daysScroll: {
    marginBottom: 16,
  },
  dayChip: {
    marginRight: 8,
  },
  activityItem: {
    marginVertical: 8,
    padding: 8,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
  },
  activityName: {
    fontSize: 16,
    marginBottom: 4,
  },
  focusText: {
    fontStyle: 'italic',
    marginBottom: 8,
  },
});

export default ExerciseScreen;
