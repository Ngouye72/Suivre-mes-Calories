import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  Restaurant,
  WbSunny,
  Psychology,
  EmojiPeople,
  LocalDining,
  Schedule
} from '@mui/icons-material';

import NutrientChart from './charts/NutrientChart';
import BehaviorAnalysis from './analysis/BehaviorAnalysis';
import WeatherImpact from './analysis/WeatherImpact';
import MealPreparation from './analysis/MealPreparation';
import CircadianAnalysis from './analysis/CircadianAnalysis';
import SocialDining from './analysis/SocialDining';
import SeasonalTrends from './analysis/SeasonalTrends';

const Dashboard = () => {
  const theme = useTheme();
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const analysisComponents = [
    { icon: <Timeline />, component: <NutrientChart />, label: "Nutrition" },
    { icon: <Psychology />, component: <BehaviorAnalysis />, label: "Comportement" },
    { icon: <WbSunny />, component: <WeatherImpact />, label: "Météo" },
    { icon: <Restaurant />, component: <MealPreparation />, label: "Préparation" },
    { icon: <Schedule />, component: <CircadianAnalysis />, label: "Rythme" },
    { icon: <EmojiPeople />, component: <SocialDining />, label: "Social" },
    { icon: <LocalDining />, component: <SeasonalTrends />, label: "Saisons" }
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Tableau de Bord d'Analyse Nutritionnelle
      </Typography>

      <Tabs
        value={currentTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 3 }}
      >
        {analysisComponents.map((tab, index) => (
          <Tab
            key={index}
            icon={tab.icon}
            label={tab.label}
            sx={{
              minWidth: 120,
              '&.Mui-selected': {
                color: theme.palette.primary.main
              }
            }}
          />
        ))}
      </Tabs>

      <Grid container spacing={3}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%', mt: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Grid item xs={12} md={8}>
              <Card sx={{ height: '100%', minHeight: 400 }}>
                <CardContent>
                  {analysisComponents[currentTab].component}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Résumé des Insights
                      </Typography>
                      <InsightsSummary tabIndex={currentTab} />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Recommandations
                      </Typography>
                      <RecommendationsList tabIndex={currentTab} />
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

const InsightsSummary = ({ tabIndex }) => {
  // Composant à implémenter pour afficher les insights pertinents
  return (
    <Typography variant="body2" color="text.secondary">
      Analyse des tendances et patterns...
    </Typography>
  );
};

const RecommendationsList = ({ tabIndex }) => {
  // Composant à implémenter pour afficher les recommandations
  return (
    <Typography variant="body2" color="text.secondary">
      Recommandations personnalisées basées sur l'analyse...
    </Typography>
  );
};

export default Dashboard;
