import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Avatar, ProgressBar, List, Colors } from 'react-native-paper';
import { getAchievements, getChallenges, getLeaderboard } from '../services/api';

const SocialScreen = () => {
  const [achievements, setAchievements] = useState([]);
  const [challenges, setChallenges] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    loadSocialData();
  }, []);

  const loadSocialData = async () => {
    try {
      const [achievementsData, challengesData, leaderboardData] = await Promise.all([
        getAchievements(),
        getChallenges(),
        getLeaderboard()
      ]);

      setAchievements(achievementsData);
      setChallenges(challengesData);
      setLeaderboard(leaderboardData);
    } catch (error) {
      console.error('Erreur lors du chargement des données sociales:', error);
    }
  };

  const renderAchievement = (achievement) => (
    <Card style={styles.achievementCard} key={achievement.title}>
      <Card.Content style={styles.achievementContent}>
        <Title style={styles.achievementTitle}>
          {achievement.icon} {achievement.title}
        </Title>
        <Paragraph>{achievement.description}</Paragraph>
      </Card.Content>
    </Card>
  );

  const renderChallenge = (challenge) => (
    <Card style={styles.challengeCard} key={challenge.id}>
      <Card.Content>
        <Title style={styles.challengeTitle}>
          {challenge.icon} {challenge.title}
        </Title>
        <Paragraph>{challenge.description}</Paragraph>
        <Paragraph style={styles.rewardText}>
          Récompense: {challenge.reward}
        </Paragraph>
        <ProgressBar
          progress={challenge.progress}
          color={Colors.blue500}
          style={styles.progressBar}
        />
        <Paragraph style={styles.progressText}>
          {Math.round(challenge.progress * 100)}% complété
        </Paragraph>
      </Card.Content>
    </Card>
  );

  const renderLeaderboardItem = (entry, index) => (
    <List.Item
      key={entry.user_id}
      title={entry.username}
      description={`Score: ${entry.score} | Série: ${entry.streak} jours`}
      left={() => (
        <View style={styles.rankContainer}>
          <Title style={styles.rankText}>#{entry.rank}</Title>
        </View>
      )}
      right={() => (
        <View style={styles.scoreContainer}>
          <Avatar.Text
            size={40}
            label={entry.achievements.toString()}
            style={styles.achievementsAvatar}
          />
        </View>
      )}
      style={[
        styles.leaderboardItem,
        index < 3 ? styles.topThree : null
      ]}
    />
  );

  return (
    <ScrollView style={styles.container}>
      <Title style={styles.sectionTitle}>Vos succès</Title>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {achievements.map(renderAchievement)}
      </ScrollView>

      <Title style={styles.sectionTitle}>Défis en cours</Title>
      {challenges.map(renderChallenge)}

      <Title style={styles.sectionTitle}>Classement</Title>
      <Card style={styles.leaderboardCard}>
        <Card.Content>
          {leaderboard.map((entry, index) => renderLeaderboardItem(entry, index))}
        </Card.Content>
      </Card>
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
  achievementCard: {
    marginRight: 16,
    width: 300,
  },
  achievementContent: {
    minHeight: 120,
  },
  achievementTitle: {
    fontSize: 18,
  },
  challengeCard: {
    marginBottom: 16,
  },
  challengeTitle: {
    fontSize: 18,
  },
  rewardText: {
    marginTop: 8,
    fontStyle: 'italic',
  },
  progressBar: {
    marginVertical: 8,
    height: 8,
    borderRadius: 4,
  },
  progressText: {
    textAlign: 'right',
    fontSize: 12,
    color: Colors.grey600,
  },
  leaderboardCard: {
    marginBottom: 16,
  },
  leaderboardItem: {
    borderBottomWidth: 1,
    borderBottomColor: Colors.grey200,
  },
  rankContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.grey200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rankText: {
    fontSize: 16,
  },
  scoreContainer: {
    justifyContent: 'center',
  },
  achievementsAvatar: {
    backgroundColor: Colors.blue500,
  },
  topThree: {
    backgroundColor: Colors.yellow50,
  },
});

export default SocialScreen;
