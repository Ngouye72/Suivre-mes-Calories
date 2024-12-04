import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Button, SegmentedButtons, TextInput } from 'react-native-paper';

const GoalSettings = ({ onSave, initialGoals }) => {
  const [goals, setGoals] = useState({
    type: 'maintien',
    weeklyChange: '0.5',
    targetWeight: '',
    deadline: '',
  });

  useEffect(() => {
    if (initialGoals) {
      setGoals(initialGoals);
    }
  }, [initialGoals]);

  const handleSave = () => {
    onSave(goals);
  };

  const calculateDailyCalories = () => {
    const baseCalories = 2000; // À remplacer par le calcul réel basé sur le profil
    let adjustment = 0;

    switch (goals.type) {
      case 'perte':
        // 1kg = 7700 calories
        adjustment = -(7700 * parseFloat(goals.weeklyChange)) / 7;
        break;
      case 'prise':
        adjustment = (7700 * parseFloat(goals.weeklyChange)) / 7;
        break;
    }

    return Math.round(baseCalories + adjustment);
  };

  return (
    <Card style={styles.container}>
      <Card.Content>
        <Title>Objectif</Title>
        
        <SegmentedButtons
          value={goals.type}
          onValueChange={(value) => setGoals({ ...goals, type: value })}
          buttons={[
            { value: 'perte', label: 'Perte' },
            { value: 'maintien', label: 'Maintien' },
            { value: 'prise', label: 'Prise' },
          ]}
          style={styles.segmentedButton}
        />

        {goals.type !== 'maintien' && (
          <>
            <Title style={styles.subtitle}>Rythme hebdomadaire</Title>
            <SegmentedButtons
              value={goals.weeklyChange}
              onValueChange={(value) => setGoals({ ...goals, weeklyChange: value })}
              buttons={[
                { value: '0.25', label: '0.25 kg' },
                { value: '0.5', label: '0.5 kg' },
                { value: '1', label: '1 kg' },
              ]}
              style={styles.segmentedButton}
            />

            <TextInput
              label="Poids cible (kg)"
              value={goals.targetWeight}
              onChangeText={(text) => setGoals({ ...goals, targetWeight: text })}
              keyboardType="numeric"
              mode="outlined"
              style={styles.input}
            />
          </>
        )}

        <View style={styles.summary}>
          <Paragraph>Calories journalières recommandées :</Paragraph>
          <Title>{calculateDailyCalories()} kcal</Title>
        </View>

        <Button
          mode="contained"
          onPress={handleSave}
          style={styles.button}
        >
          Enregistrer
        </Button>
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: 16,
  },
  subtitle: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 8,
  },
  segmentedButton: {
    marginVertical: 8,
  },
  input: {
    marginTop: 8,
  },
  summary: {
    marginTop: 16,
    alignItems: 'center',
  },
  button: {
    marginTop: 16,
  },
});

export default GoalSettings;
