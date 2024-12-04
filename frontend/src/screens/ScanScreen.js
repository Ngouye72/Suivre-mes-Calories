import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { RNCamera } from 'react-native-camera';
import { Button, ActivityIndicator } from 'react-native-paper';
import { searchFoodByBarcode } from '../services/api';

const ScanScreen = ({ navigation }) => {
  const [scanning, setScanning] = useState(false);

  const onBarCodeRead = async ({ data }) => {
    if (scanning) return;
    
    setScanning(true);
    try {
      const foodData = await searchFoodByBarcode(data);
      if (foodData) {
        navigation.navigate('Journal', { foodData });
      } else {
        Alert.alert(
          'Produit non trouvé',
          'Désolé, ce produit n\'est pas dans notre base de données.'
        );
      }
    } catch (error) {
      Alert.alert(
        'Erreur',
        'Une erreur est survenue lors de la recherche du produit.'
      );
    } finally {
      setScanning(false);
    }
  };

  return (
    <View style={styles.container}>
      <RNCamera
        style={styles.camera}
        type={RNCamera.Constants.Type.back}
        onBarCodeRead={onBarCodeRead}
        captureAudio={false}
      >
        <View style={styles.overlay}>
          {scanning && (
            <ActivityIndicator
              animating={true}
              size="large"
              color="#ffffff"
            />
          )}
        </View>
      </RNCamera>
      <View style={styles.buttonContainer}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('Journal')}
        >
          Saisie manuelle
        </Button>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  buttonContainer: {
    padding: 16,
    backgroundColor: 'white',
  },
});

export default ScanScreen;
