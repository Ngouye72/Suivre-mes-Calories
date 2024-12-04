import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Grid
} from '@mui/material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const NutrientChart = () => {
  const [timeRange, setTimeRange] = useState('week');

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  // Données simulées pour le graphique
  const nutrientData = [
    { date: 'Lun', calories: 2100, protéines: 75, glucides: 250, lipides: 70 },
    { date: 'Mar', calories: 1950, protéines: 80, glucides: 230, lipides: 65 },
    { date: 'Mer', calories: 2200, protéines: 85, glucides: 260, lipides: 75 },
    { date: 'Jeu', calories: 2050, protéines: 78, glucides: 240, lipides: 68 },
    { date: 'Ven', calories: 2150, protéines: 82, glucides: 255, lipides: 72 },
    { date: 'Sam', calories: 2300, protéines: 88, glucides: 270, lipides: 78 },
    { date: 'Dim', calories: 2250, protéines: 85, glucides: 265, lipides: 75 }
  ];

  const macronutrientDistribution = [
    { name: 'Protéines', value: 25 },
    { name: 'Glucides', value: 50 },
    { name: 'Lipides', value: 25 }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">
          Analyse Nutritionnelle
        </Typography>
        <ToggleButtonGroup
          value={timeRange}
          exclusive
          onChange={handleTimeRangeChange}
          size="small"
        >
          <ToggleButton value="week">Semaine</ToggleButton>
          <ToggleButton value="month">Mois</ToggleButton>
          <ToggleButton value="year">Année</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Évolution des Apports
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={nutrientData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="calories"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                    />
                    <Area
                      type="monotone"
                      dataKey="protéines"
                      stackId="2"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                    />
                    <Area
                      type="monotone"
                      dataKey="glucides"
                      stackId="3"
                      stroke="#ffc658"
                      fill="#ffc658"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Répartition des Macronutriments
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={macronutrientDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name} ${value}%`}
                    >
                      {macronutrientDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Objectifs Nutritionnels
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Calories quotidiennes : 2000 kcal
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Protéines : 80g (20%)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Glucides : 250g (50%)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Lipides : 67g (30%)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NutrientChart;
