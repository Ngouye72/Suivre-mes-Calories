import React, { useState } from 'react';
import { StyleSheet, View, Dimensions } from 'react-native';
import { RNCamera } from 'react-native-camera';
import { ActivityIndicator, Text } from 'react-native-paper';

const BarcodeScanner = ({ onBarcodeDetected, scanning }) => {
  const [camera, setCamera] = useState(null);

  const handleBarCodeRead = ({ data, type }) => {
    if (!scanning) {
      onBarcodeDetected(data);
    }
  };

  return (
    <View style={styles.container}>
      <RNCamera
        ref={ref => setCamera(ref)}
        style={styles.camera}
        type={RNCamera.Constants.Type.back}
        onBarCodeRead={handleBarCodeRead}
        barCodeTypes={[RNCamera.Constants.BarCodeType.ean13, RNCamera.Constants.BarCodeType.ean8]}
        androidCameraPermissionOptions={{
          title: 'Permission d\'utiliser la caméra',
          message: 'Nous avons besoin de votre permission pour utiliser la caméra',
          buttonPositive: 'Ok',
          buttonNegative: 'Annuler',
        }}
      >
        <View style={styles.overlay}>
          <View style={styles.scanArea} />
          {scanning && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#ffffff" />
              <Text style={styles.loadingText}>Recherche du produit...</Text>
            </View>
          )}
        </View>
      </RNCamera>
    </View>
  );
};

const { width } = Dimensions.get('window');
const scanAreaSize = width * 0.7;

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: scanAreaSize,
    height: scanAreaSize,
    borderWidth: 2,
    borderColor: '#ffffff',
    backgroundColor: 'transparent',
  },
  loadingContainer: {
    position: 'absolute',
    top: '60%',
    alignItems: 'center',
  },
  loadingText: {
    color: '#ffffff',
    marginTop: 10,
  },
});

export default BarcodeScanner;
