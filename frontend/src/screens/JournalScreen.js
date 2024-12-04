import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { FAB, List, Searchbar, Portal, Modal, Button, TextInput } from 'react-native-paper';
import { getFoodEntries, addFoodEntry } from '../services/api';

const JournalScreen = () => {
  const [entries, setEntries] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [visible, setVisible] = useState(false);
  const [newEntry, setNewEntry] = useState({
    foodName: '',
    calories: '',
    proteins: '',
    carbs: '',
    fats: '',
  });

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    try {
      const data = await getFoodEntries();
      setEntries(data);
    } catch (error) {
      console.error('Erreur lors du chargement des entrées:', error);
    }
  };

  const handleAddEntry = async () => {
    try {
      await addFoodEntry({
        ...newEntry,
        calories: parseInt(newEntry.calories),
        proteins: parseFloat(newEntry.proteins),
        carbs: parseFloat(newEntry.carbs),
        fats: parseFloat(newEntry.fats),
      });
      setVisible(false);
      loadEntries();
    } catch (error) {
      console.error('Erreur lors de l\'ajout de l\'entrée:', error);
    }
  };

  const renderItem = ({ item }) => (
    <List.Item
      title={item.foodName}
      description={`${item.calories} cal | P: ${item.proteins}g | G: ${item.carbs}g | L: ${item.fats}g`}
      left={props => <List.Icon {...props} icon="food" />}
    />
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Rechercher un aliment"
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={entries}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
      />

      <Portal>
        <Modal
          visible={visible}
          onDismiss={() => setVisible(false)}
          contentContainerStyle={styles.modal}>
          <TextInput
            label="Nom de l'aliment"
            value={newEntry.foodName}
            onChangeText={text => setNewEntry({...newEntry, foodName: text})}
            style={styles.input}
          />
          <TextInput
            label="Calories"
            value={newEntry.calories}
            onChangeText={text => setNewEntry({...newEntry, calories: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <TextInput
            label="Protéines (g)"
            value={newEntry.proteins}
            onChangeText={text => setNewEntry({...newEntry, proteins: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <TextInput
            label="Glucides (g)"
            value={newEntry.carbs}
            onChangeText={text => setNewEntry({...newEntry, carbs: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <TextInput
            label="Lipides (g)"
            value={newEntry.fats}
            onChangeText={text => setNewEntry({...newEntry, fats: text})}
            keyboardType="numeric"
            style={styles.input}
          />
          <Button mode="contained" onPress={handleAddEntry} style={styles.button}>
            Ajouter
          </Button>
        </Modal>
      </Portal>

      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => setVisible(true)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchbar: {
    margin: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
});

export default JournalScreen;
