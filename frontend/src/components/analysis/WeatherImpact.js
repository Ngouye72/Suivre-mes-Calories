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
  ListItemIcon
} from '@mui/material';
import {
  WbSunny,
  Opacity,
  AcUnit,
  Thermostat
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';

const WeatherImpact = () => {
  // Données simulées pour les graphiques
  const weatherData = [
    { date: '01/02', température: 22, calories: 2100, hydratation: 2.5 },
    { date: '02/02', température: 24, calories: 1950, hydratation: 2.8 },
    { date: '03/02', température: 20, calories: 2200, hydratation: 2.2 },
    { date: '04/02', température: 18, calories: 2300, hydratation: 2.0 },
    { date: '05/02', température: 25, calories: 1900, hydratation: 3.0 },
    { date: '06/02', température: 23, calories: 2000, hydratation: 2.6 },
    { date: '07/02', température: 21, calories: 2150, hydratation: 2.4 }
  ];

  const correlationData = [
    { température: 18, calories: 2300, z: 1 },
    { température: 20, calories: 2200, z: 1 },
    { température: 22, calories: 2100, z: 1 },
    { température: 24, calories: 1950, z: 1 },
    { température: 25, calories: 1900, z: 1 }
  ];

  const weatherImpacts = [
    {
      icon: <Thermostat />,
      condition: "Température",
      impact: "Les températures élevées réduisent l'appétit"
    },
    {
      icon: <Opacity />,
      condition: "Humidité",
      impact: "L'humidité influence les besoins en hydratation"
    },
    {
      icon: <WbSunny />,
      condition: "Ensoleillement",
      impact: "Plus d'énergie et de repas légers les jours ensoleillés"
    },
    {
      icon: <AcUnit />,
      condition: "Saison",
      impact: "Préférence pour les plats chauds en hiver"
    }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Impact de la Météo
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Corrélation Température-Calories
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weatherData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="température"
                      stroke="#ff7300"
                      name="Température (°C)"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="calories"
                      stroke="#82ca9d"
                      name="Calories"
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
                Tendances Météorologiques
              </Typography>
              <List>
                {weatherImpacts.map((impact, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {impact.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={impact.condition}
                      secondary={impact.impact}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patterns de Corrélation
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid />
                    <XAxis type="number" dataKey="température" name="Température" unit="°C" />
                    <YAxis type="number" dataKey="calories" name="Calories" />
                    <ZAxis type="number" dataKey="z" range={[100]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter
                      name="Température vs Calories"
                      data={correlationData}
                      fill="#8884d8"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WeatherImpact;
