import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Title, Snackbar, SegmentedButtons } from 'react-native-paper';
import { register } from '../services/api';

const RegisterScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    weight: '',
    height: '',
    age: '',
    gender: 'homme',
    activityLevel: 'sedentaire',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    // Validation de base
    if (!formData.email || !formData.password || !formData.username) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      navigation.replace('Login');
    } catch (err) {
      setError('Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>Créer un compte</Title>

      <TextInput
        label="Nom d'utilisateur"
        value={formData.username}
        onChangeText={(text) => updateFormData('username', text)}
        mode="outlined"
        style={styles.input}
      />

      <TextInput
        label="Email"
        value={formData.email}
        onChangeText={(text) => updateFormData('email', text)}
        mode="outlined"
        keyboardType="email-address"
        autoCapitalize="none"
        style={styles.input}
      />

      <TextInput
        label="Mot de passe"
        value={formData.password}
        onChangeText={(text) => updateFormData('password', text)}
        mode="outlined"
        secureTextEntry
        style={styles.input}
      />

      <TextInput
        label="Confirmer le mot de passe"
        value={formData.confirmPassword}
        onChangeText={(text) => updateFormData('confirmPassword', text)}
        mode="outlined"
        secureTextEntry
        style={styles.input}
      />

      <Title style={styles.subtitle}>Informations physiques</Title>

      <TextInput
        label="Poids (kg)"
        value={formData.weight}
        onChangeText={(text) => updateFormData('weight', text)}
        mode="outlined"
        keyboardType="numeric"
        style={styles.input}
      />

      <TextInput
        label="Taille (cm)"
        value={formData.height}
        onChangeText={(text) => updateFormData('height', text)}
        mode="outlined"
        keyboardType="numeric"
        style={styles.input}
      />

      <TextInput
        label="Âge"
        value={formData.age}
        onChangeText={(text) => updateFormData('age', text)}
        mode="outlined"
        keyboardType="numeric"
        style={styles.input}
      />

      <Title style={styles.subtitle}>Genre</Title>
      <SegmentedButtons
        value={formData.gender}
        onValueChange={(value) => updateFormData('gender', value)}
        buttons={[
          { value: 'homme', label: 'Homme' },
          { value: 'femme', label: 'Femme' },
        ]}
        style={styles.segmentedButton}
      />

      <Title style={styles.subtitle}>Niveau d'activité</Title>
      <SegmentedButtons
        value={formData.activityLevel}
        onValueChange={(value) => updateFormData('activityLevel', value)}
        buttons={[
          { value: 'sedentaire', label: 'Sédentaire' },
          { value: 'modere', label: 'Modéré' },
          { value: 'actif', label: 'Actif' },
        ]}
        style={styles.segmentedButton}
      />

      <Button
        mode="contained"
        onPress={handleRegister}
        loading={loading}
        style={styles.button}
      >
        S'inscrire
      </Button>

      <Button
        mode="text"
        onPress={() => navigation.navigate('Login')}
        style={styles.button}
      >
        Déjà un compte ? Se connecter
      </Button>

      <Snackbar
        visible={!!error}
        onDismiss={() => setError('')}
        duration={3000}
      >
        {error}
      </Snackbar>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    marginTop: 20,
    marginBottom: 10,
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
  },
  segmentedButton: {
    marginBottom: 15,
  },
});

export default RegisterScreen;
