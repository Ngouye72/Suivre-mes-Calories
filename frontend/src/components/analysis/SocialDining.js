import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Line,
  Scatter
} from 'recharts';
import {
  Group,
  Restaurant,
  Timer,
  TrendingUp
} from '@mui/icons-material';

const SocialDining = () => {
  // Données simulées pour les graphiques
  const socialMealData = [
    { type: 'Seul', calories: 1800, durée: 20, satisfaction: 75 },
    { type: 'Famille', calories: 2200, durée: 45, satisfaction: 90 },
    { type: 'Amis', calories: 2400, durée: 60, satisfaction: 95 },
    { type: 'Collègues', calories: 2000, durée: 30, satisfaction: 80 },
    { type: 'Restaurant', calories: 2500, durée: 75, satisfaction: 85 }
  ];

  const mealSizeData = [
    { groupSize: '1', portion: 100, conversation: 0 },
    { groupSize: '2', portion: 120, conversation: 30 },
    { groupSize: '3-4', portion: 135, conversation: 50 },
    { groupSize: '5+', portion: 150, conversation: 70 }
  ];

  const socialPatterns = [
    {
      context: 'Repas en Famille',
      caractéristiques: [
        'Portions plus équilibrées',
        'Repas plus longs',
        'Meilleure satisfaction'
      ]
    },
    {
      context: 'Sorties entre Amis',
      caractéristiques: [
        'Portions plus importantes',
        'Plus de variété',
        'Influence des choix mutuels'
      ]
    },
    {
      context: 'Déjeuners Professionnels',
      caractéristiques: [
        'Temps limité',
        'Choix plus santé',
        'Portions modérées'
      ]
    }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analyse des Repas Sociaux
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Impact du Contexte Social
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={socialMealData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar
                      yAxisId="left"
                      dataKey="calories"
                      fill="#8884d8"
                      name="Calories"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="satisfaction"
                      stroke="#82ca9d"
                      name="Satisfaction (%)"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Taille du Groupe vs Portions
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={mealSizeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="groupSize" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="portion" fill="#8884d8" name="Taille Portion (%)" />
                    <Line
                      type="monotone"
                      dataKey="conversation"
                      stroke="#82ca9d"
                      name="Temps de Conversation (%)"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patterns Sociaux
              </Typography>
              <Grid container spacing={2}>
                {socialPatterns.map((pattern, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>
                          {pattern.context}
                        </Typography>
                        <List dense>
                          {pattern.caractéristiques.map((carac, idx) => (
                            <ListItem key={idx}>
                              <ListItemAvatar>
                                <Avatar>
                                  {idx === 0 ? <Group /> : 
                                   idx === 1 ? <Restaurant /> : 
                                   <TrendingUp />}
                                </Avatar>
                              </ListItemAvatar>
                              <ListItemText primary={carac} />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommandations Sociales
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip
                  icon={<Timer />}
                  label="Prenez le temps de manger en société"
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  icon={<Restaurant />}
                  label="Choisissez des restaurants équilibrés"
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  icon={<Group />}
                  label="Partagez des repas en famille"
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  icon={<TrendingUp />}
                  label="Restez conscient des portions"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SocialDining;
