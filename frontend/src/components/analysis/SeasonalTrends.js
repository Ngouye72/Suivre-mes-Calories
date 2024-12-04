import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const SeasonalTrends = () => {
  // Données simulées pour les graphiques
  const seasonalData = [
    { mois: 'Jan', calories: 2300, protéines: 85, glucides: 280, lipides: 75 },
    { mois: 'Fév', calories: 2250, protéines: 82, glucides: 270, lipides: 73 },
    { mois: 'Mar', calories: 2200, protéines: 80, glucides: 260, lipides: 70 },
    { mois: 'Avr', calories: 2100, protéines: 75, glucides: 250, lipides: 65 },
    { mois: 'Mai', calories: 2000, protéines: 73, glucides: 240, lipides: 62 },
    { mois: 'Juin', calories: 1900, protéines: 70, glucides: 230, lipides: 58 }
  ];

  const foodTypeDistribution = {
    hiver: [
      { name: 'Plats chauds', value: 45 },
      { name: 'Soupes', value: 25 },
      { name: 'Féculents', value: 20 },
      { name: 'Autres', value: 10 }
    ],
    été: [
      { name: 'Salades', value: 35 },
      { name: 'Grillades', value: 30 },
      { name: 'Fruits', value: 25 },
      { name: 'Autres', value: 10 }
    ]
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const seasonalRecommendations = {
    printemps: [
      'Légumes de saison frais',
      'Herbes aromatiques fraîches',
      'Fruits printaniers'
    ],
    été: [
      'Hydratation renforcée',
      'Repas légers et frais',
      'Fruits d\'été'
    ],
    automne: [
      'Légumes racines',
      'Courges et potirons',
      'Fruits d\'automne'
    ],
    hiver: [
      'Soupes nourrissantes',
      'Légumineuses',
      'Agrumes'
    ]
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Tendances Saisonnières
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Évolution Saisonnière des Apports
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={seasonalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="mois" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="calories"
                      stroke="#8884d8"
                      name="Calories"
                    />
                    <Line
                      type="monotone"
                      dataKey="protéines"
                      stroke="#82ca9d"
                      name="Protéines"
                    />
                    <Line
                      type="monotone"
                      dataKey="glucides"
                      stroke="#ffc658"
                      name="Glucides"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Distribution des Types d'Aliments
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={foodTypeDistribution.hiver}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name} ${value}%`}
                    >
                      {foodTypeDistribution.hiver.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommandations Saisonnières
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(seasonalRecommendations).map(([season, recs]) => (
                  <Grid item xs={12} sm={6} md={3} key={season}>
                    <Typography variant="subtitle1" gutterBottom>
                      {season.charAt(0).toUpperCase() + season.slice(1)}
                    </Typography>
                    <List dense>
                      {recs.map((rec, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={
                              <Chip
                                label={rec}
                                variant="outlined"
                                size="small"
                                color="primary"
                              />
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SeasonalTrends;
