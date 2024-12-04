import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Stack
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
  RadialBarChart,
  RadialBar
} from 'recharts';

const CircadianAnalysis = () => {
  // Données simulées pour les graphiques
  const hourlyIntake = [
    { heure: '6h', calories: 300, type: 'Petit-déjeuner' },
    { heure: '9h', calories: 150, type: 'Collation' },
    { heure: '12h', calories: 650, type: 'Déjeuner' },
    { heure: '16h', calories: 200, type: 'Goûter' },
    { heure: '19h', calories: 550, type: 'Dîner' },
    { heure: '22h', calories: 100, type: 'Collation nocturne' }
  ];

  const metabolicWindows = [
    {
      name: 'Petit-déjeuner',
      efficacité: 90,
      fill: '#8884d8',
      période: '6h-8h'
    },
    {
      name: 'Déjeuner',
      efficacité: 85,
      fill: '#83a6ed',
      période: '12h-14h'
    },
    {
      name: 'Dîner',
      efficacité: 70,
      fill: '#8dd1e1',
      période: '19h-21h'
    },
    {
      name: 'Collations',
      efficacité: 60,
      fill: '#82ca9d',
      période: 'Variables'
    }
  ];

  const chronotypeInfo = {
    type: 'Intermédiaire',
    périodesOptimales: [
      { période: 'Petit-déjeuner', horaire: '7h-8h30' },
      { période: 'Déjeuner', horaire: '12h30-14h' },
      { période: 'Dîner', horaire: '19h-20h30' }
    ],
    recommandations: [
      'Maintenir des horaires de repas réguliers',
      'Éviter les repas tardifs',
      'Respecter une fenêtre de jeûne de 12h'
    ]
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analyse du Rythme Circadien
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Distribution Horaire des Repas
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hourlyIntake}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="heure" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="calories"
                      fill="#8884d8"
                      name="Calories"
                      label={{ position: 'top' }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fenêtres Métaboliques
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="20%"
                    outerRadius="80%"
                    data={metabolicWindows}
                    startAngle={180}
                    endAngle={0}
                  >
                    <RadialBar
                      minAngle={15}
                      label={{ fill: '#666', position: 'insideStart' }}
                      background
                      clockWise={true}
                      dataKey="efficacité"
                    />
                    <Legend
                      iconSize={10}
                      width={120}
                      height={140}
                      layout="vertical"
                      verticalAlign="middle"
                      align="right"
                    />
                    <Tooltip />
                  </RadialBarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profil Chronotype
              </Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Type: {chronotypeInfo.type}
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    {chronotypeInfo.périodesOptimales.map((période, index) => (
                      <Chip
                        key={index}
                        label={`${période.période}: ${période.horaire}`}
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </Box>
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Recommandations:
                  </Typography>
                  {chronotypeInfo.recommandations.map((rec, index) => (
                    <Typography key={index} variant="body2" color="text.secondary" paragraph>
                      • {rec}
                    </Typography>
                  ))}
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CircadianAnalysis;
