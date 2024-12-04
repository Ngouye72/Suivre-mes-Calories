import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, IconButton, Colors, Badge } from 'react-native-paper';
import { getUserNotifications } from '../services/api';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    // Rafraîchir les notifications toutes les 5 minutes
    const interval = setInterval(loadNotifications, 300000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await getUserNotifications();
      setNotifications(data);
      setUnreadCount(data.filter(n => !n.read).length);
    } catch (error) {
      console.error('Erreur lors du chargement des notifications:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'meal_reminder':
        return 'food-fork-drink';
      case 'goal_alert':
        return 'target';
      case 'achievement':
        return 'trophy';
      default:
        return 'bell';
    }
  };

  const getNotificationColor = (priority) => {
    switch (priority) {
      case 'high':
        return Colors.red500;
      case 'medium':
        return Colors.orange500;
      case 'low':
        return Colors.green500;
      default:
        return Colors.grey500;
    }
  };

  const renderNotification = (notification) => (
    <Card 
      style={[
        styles.notificationCard,
        notification.read ? styles.readNotification : styles.unreadNotification
      ]}
      key={notification.id}
    >
      <Card.Content style={styles.notificationContent}>
        <IconButton
          icon={getNotificationIcon(notification.type)}
          color={getNotificationColor(notification.priority)}
          size={24}
          style={styles.icon}
        />
        <View style={styles.textContainer}>
          <Paragraph>{notification.message}</Paragraph>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Title>Notifications</Title>
        {unreadCount > 0 && (
          <Badge style={styles.badge}>
            {unreadCount}
          </Badge>
        )}
      </View>

      <ScrollView style={styles.notificationsList}>
        {notifications.map(renderNotification)}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    elevation: 4,
  },
  badge: {
    marginLeft: 8,
  },
  notificationsList: {
    padding: 8,
  },
  notificationCard: {
    marginBottom: 8,
  },
  notificationContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    margin: 0,
  },
  textContainer: {
    flex: 1,
    marginLeft: 8,
  },
  unreadNotification: {
    backgroundColor: '#fff',
  },
  readNotification: {
    backgroundColor: '#f8f8f8',
    opacity: 0.8,
  },
});

export default NotificationCenter;
