import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Card, Title, Paragraph } from 'react-native-paper';
import { getUserProfile, updateUserProfile } from '../services/api';

const ProfileScreen = () => {
  const [profile, setProfile] = useState({
    weight: '',
    height: '',
    age: '',
    gender: '',
    activityLevel: '',
    goal: '',
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await getUserProfile();
      setProfile(data);
    } catch (error) {
      console.error('Erreur lors du chargement du profil:', error);
    }
  };

  const handleUpdate = async () => {
    try {
      await updateUserProfile(profile);
      // Recharger les données du profil
      loadProfile();
    } catch (error) {
      console.error('Erreur lors de la mise à jour du profil:', error);
    }
  };

  const calculateBMR = () => {
    // Formule de Mifflin-St Jeor
    const weight = parseFloat(profile.weight);
    const height = parseFloat(profile.height);
    const age = parseInt(profile.age);
    
    if (profile.gender === 'homme') {
      return (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
      return (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }
  };

  const getActivityMultiplier = () => {
    const levels = {
      sedentaire: 1.2,
      leger: 1.375,
      modere: 1.55,
      actif: 1.725,
      tresActif: 1.9,
    };
    return levels[profile.activityLevel] || 1.2;
  };

  const calculateTDEE = () => {
    return calculateBMR() * getActivityMultiplier();
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Informations personnelles</Title>
          <TextInput
            label="Poids (kg)"
            value={profile.weight}
            onChangeText={text => setProfile({...profile, weight: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <TextInput
            label="Taille (cm)"
            value={profile.height}
            onChangeText={text => setProfile({...profile, height: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <TextInput
            label="Âge"
            value={profile.age}
            onChangeText={text => setProfile({...profile, age: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <Button
            mode="contained"
            onPress={handleUpdate}
            style={styles.button}
          >
            Mettre à jour
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Métabolisme</Title>
          <Paragraph>Métabolisme de base: {calculateBMR().toFixed(0)} calories</Paragraph>
          <Paragraph>Dépense quotidienne: {calculateTDEE().toFixed(0)} calories</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Objectifs</Title>
          <TextInput
            label="Objectif de poids"
            value={profile.goal}
            onChangeText={text => setProfile({...profile, goal: text})}
            style={styles.input}
          />
          <Button
            mode="contained"
            onPress={handleUpdate}
            style={styles.button}
          >
            Enregistrer
          </Button>
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
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
});

export default ProfileScreen;
