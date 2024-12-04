import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress
} from '@mui/material';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer
} from 'recharts';

const BehaviorAnalysis = () => {
  // Données simulées pour le graphique radar
  const behaviorData = [
    { aspect: 'Alimentation Émotionnelle', value: 65 },
    { aspect: 'Alimentation Sociale', value: 80 },
    { aspect: 'Alimentation Consciente', value: 70 },
    { aspect: 'Gestion du Stress', value: 60 },
    { aspect: 'Régularité', value: 75 },
    { aspect: 'Équilibre', value: 85 }
  ];

  const mealPatterns = [
    { type: 'Repas Équilibrés', value: 75 },
    { type: 'Collations Saines', value: 65 },
    { type: 'Portions Adaptées', value: 80 }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analyse Comportementale
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profil Comportemental
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={behaviorData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="aspect" />
                    <Radar
                      name="Comportement"
                      dataKey="value"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patterns de Repas
              </Typography>
              {mealPatterns.map((pattern, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    {pattern.type}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={pattern.value}
                        sx={{
                          height: 10,
                          borderRadius: 5
                        }}
                      />
                    </Box>
                    <Box sx={{ minWidth: 35 }}>
                      <Typography variant="body2" color="text.secondary">
                        {`${Math.round(pattern.value)}%`}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommandations Comportementales
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Pratiquez la pleine conscience pendant les repas
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Établissez des horaires de repas réguliers
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Identifiez les déclencheurs émotionnels
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BehaviorAnalysis;
