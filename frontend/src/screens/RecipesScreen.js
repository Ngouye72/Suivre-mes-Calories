import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Chip, Button, ActivityIndicator } from 'react-native-paper';
import { getRecipeSuggestions, getWeeklyMealPlan } from '../services/api';

const RecipesScreen = () => {
  const [loading, setLoading] = useState(true);
  const [recipes, setRecipes] = useState([]);
  const [mealType, setMealType] = useState(null);

  useEffect(() => {
    loadRecipes();
  }, [mealType]);

  const loadRecipes = async () => {
    setLoading(true);
    try {
      const data = await getRecipeSuggestions(mealType);
      setRecipes(data);
    } catch (error) {
      console.error('Erreur lors du chargement des recettes:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderRecipeCard = (recipe) => (
    <Card style={styles.card} key={recipe.name}>
      <Card.Content>
        <Title>{recipe.name}</Title>
        <Paragraph>
          {recipe.calories} kcal | P: {recipe.proteins}g | G: {recipe.carbs}g | L: {recipe.fats}g
        </Paragraph>

        <View style={styles.tagsContainer}>
          {recipe.tags.map((tag, index) => (
            <Chip key={index} style={styles.tag}>{tag}</Chip>
          ))}
        </View>

        <Title style={styles.subtitle}>Ingrédients</Title>
        {recipe.ingredients.map((ingredient, index) => (
          <Paragraph key={index}>• {ingredient}</Paragraph>
        ))}

        <Title style={styles.subtitle}>Instructions</Title>
        {recipe.instructions.map((instruction, index) => (
          <Paragraph key={index}>{index + 1}. {instruction}</Paragraph>
        ))}

        <View style={styles.metaInfo}>
          <Paragraph>Temps de préparation: {recipe.preparation_time} min</Paragraph>
          <Paragraph>Difficulté: {recipe.difficulty}</Paragraph>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <Chip
            selected={mealType === null}
            onPress={() => setMealType(null)}
            style={styles.filterChip}
          >
            Tous
          </Chip>
          <Chip
            selected={mealType === 'petit-dejeuner'}
            onPress={() => setMealType('petit-dejeuner')}
            style={styles.filterChip}
          >
            Petit-déjeuner
          </Chip>
          <Chip
            selected={mealType === 'dejeuner'}
            onPress={() => setMealType('dejeuner')}
            style={styles.filterChip}
          >
            Déjeuner
          </Chip>
          <Chip
            selected={mealType === 'diner'}
            onPress={() => setMealType('diner')}
            style={styles.filterChip}
          >
            Dîner
          </Chip>
          <Chip
            selected={mealType === 'collation'}
            onPress={() => setMealType('collation')}
            style={styles.filterChip}
          >
            Collation
          </Chip>
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator style={styles.loading} />
      ) : (
        <ScrollView style={styles.recipesList}>
          {recipes.map(recipe => renderRecipeCard(recipe))}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  filterContainer: {
    padding: 10,
    backgroundColor: 'white',
    elevation: 4,
  },
  filterChip: {
    marginRight: 8,
  },
  recipesList: {
    padding: 10,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginVertical: 10,
  },
  tag: {
    marginRight: 8,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    marginTop: 16,
    marginBottom: 8,
  },
  metaInfo: {
    marginTop: 16,
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default RecipesScreen;
