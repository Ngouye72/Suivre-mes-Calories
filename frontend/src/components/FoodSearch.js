import React, { useState, useCallback } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Searchbar, List, ActivityIndicator } from 'react-native-paper';
import debounce from 'lodash/debounce';
import { searchFood } from '../services/api';

const FoodSearch = ({ onFoodSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const performSearch = useCallback(
    debounce(async (query) => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const data = await searchFood(query);
        setResults(data);
      } catch (error) {
        console.error('Erreur de recherche:', error);
      } finally {
        setLoading(false);
      }
    }, 500),
    []
  );

  const handleSearch = (query) => {
    setSearchQuery(query);
    performSearch(query);
  };

  const renderItem = ({ item }) => (
    <List.Item
      title={item.name}
      description={`${item.calories} kcal | P: ${item.proteins}g | G: ${item.carbs}g | L: ${item.fats}g`}
      left={props => <List.Icon {...props} icon="food" />}
      onPress={() => onFoodSelect(item)}
    />
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Rechercher un aliment"
        onChangeText={handleSearch}
        value={searchQuery}
        style={styles.searchBar}
      />

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
        <FlatList
          data={results}
          renderItem={renderItem}
          keyExtractor={item => item.id.toString()}
          style={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  searchBar: {
    margin: 16,
    elevation: 4,
  },
  list: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default FoodSearch;
