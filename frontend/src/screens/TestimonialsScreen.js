import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, Image } from 'react-native';
import { Card, Title, Paragraph, Button, Chip, Avatar, IconButton, Colors } from 'react-native-paper';
import { getFeaturedTestimonials, getSuccessStories, getTipsByCategory } from '../services/api';

const TestimonialsScreen = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [tips, setTips] = useState([]);

  useEffect(() => {
    loadTestimonials();
  }, [selectedCategory]);

  const loadTestimonials = async () => {
    try {
      const data = selectedCategory
        ? await getSuccessStories(selectedCategory)
        : await getFeaturedTestimonials();
      setTestimonials(data);

      if (selectedCategory) {
        const tipsData = await getTipsByCategory(selectedCategory);
        setTips(tipsData);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des témoignages:', error);
    }
  };

  const renderTestimonialCard = (testimonial) => (
    <Card style={styles.testimonialCard} key={testimonial.user_id}>
      <Card.Content>
        <View style={styles.headerContainer}>
          <Avatar.Text
            size={40}
            label={testimonial.username.substring(0, 2).toUpperCase()}
          />
          <View style={styles.headerText}>
            <Title>{testimonial.title}</Title>
            <Paragraph style={styles.username}>par {testimonial.username}</Paragraph>
          </View>
          {testimonial.verified && (
            <IconButton
              icon="check-circle"
              color={Colors.green500}
              size={24}
            />
          )}
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Title>-{testimonial.weight_loss}kg</Title>
            <Paragraph>Perdus</Paragraph>
          </View>
          <View style={styles.statItem}>
            <Title>{testimonial.time_period}</Title>
            <Paragraph>Durée</Paragraph>
          </View>
          <View style={styles.statItem}>
            <Title>{Math.round(testimonial.success_rate)}%</Title>
            <Paragraph>Réussite</Paragraph>
          </View>
        </View>

        <Paragraph style={styles.content}>{testimonial.content}</Paragraph>

        {testimonial.tips && testimonial.tips.length > 0 && (
          <View style={styles.tipsContainer}>
            <Title style={styles.tipsTitle}>Conseils de {testimonial.username}</Title>
            {testimonial.tips.map((tip, index) => (
              <View key={index} style={styles.tipItem}>
                <IconButton
                  icon="lightbulb-outline"
                  size={20}
                  color={Colors.amber500}
                  style={styles.tipIcon}
                />
                <Paragraph style={styles.tipText}>{tip}</Paragraph>
              </View>
            ))}
          </View>
        )}

        <View style={styles.actionsContainer}>
          <Button
            icon="thumb-up"
            mode="outlined"
            onPress={() => {}}
          >
            {testimonial.likes} J'aime
          </Button>
          <Button
            icon="comment"
            mode="outlined"
            onPress={() => {}}
          >
            Commenter
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  const renderCategoryFilters = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={styles.categoriesContainer}
    >
      <Chip
        selected={selectedCategory === null}
        onPress={() => setSelectedCategory(null)}
        style={styles.categoryChip}
      >
        Tous
      </Chip>
      <Chip
        selected={selectedCategory === 'weight_loss'}
        onPress={() => setSelectedCategory('weight_loss')}
        style={styles.categoryChip}
      >
        Perte de poids
      </Chip>
      <Chip
        selected={selectedCategory === 'quick_results'}
        onPress={() => setSelectedCategory('quick_results')}
        style={styles.categoryChip}
      >
        Résultats rapides
      </Chip>
      <Chip
        selected={selectedCategory === 'maintenance'}
        onPress={() => setSelectedCategory('maintenance')}
        style={styles.categoryChip}
      >
        Maintien
      </Chip>
    </ScrollView>
  );

  const renderTips = () => {
    if (!tips.length) return null;

    return (
      <Card style={styles.tipsCard}>
        <Card.Content>
          <Title>Conseils pour {selectedCategory}</Title>
          {tips.map((tip, index) => (
            <View key={index} style={styles.tipItem}>
              <IconButton
                icon="star"
                size={20}
                color={Colors.amber500}
                style={styles.tipIcon}
              />
              <Paragraph style={styles.tipText}>{tip}</Paragraph>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  return (
    <ScrollView style={styles.container}>
      {renderCategoryFilters()}
      {tips.length > 0 && renderTips()}
      {testimonials.map(renderTestimonialCard)}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  categoriesContainer: {
    padding: 16,
    backgroundColor: 'white',
  },
  categoryChip: {
    marginRight: 8,
  },
  testimonialCard: {
    margin: 16,
    elevation: 4,
  },
  headerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerText: {
    flex: 1,
    marginLeft: 16,
  },
  username: {
    color: Colors.grey600,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 16,
    backgroundColor: Colors.grey100,
    padding: 16,
    borderRadius: 8,
  },
  statItem: {
    alignItems: 'center',
  },
  content: {
    marginVertical: 16,
    lineHeight: 24,
  },
  tipsContainer: {
    marginTop: 16,
    backgroundColor: Colors.grey100,
    padding: 16,
    borderRadius: 8,
  },
  tipsTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  tipIcon: {
    margin: 0,
    marginRight: 8,
  },
  tipText: {
    flex: 1,
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  tipsCard: {
    margin: 16,
    marginTop: 0,
    elevation: 4,
  },
});

export default TestimonialsScreen;
