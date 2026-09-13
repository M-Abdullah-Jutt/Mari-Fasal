
import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  Image,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";

import { predictFull, PlantAnalysisResult } from "../api/plantApi";
import ResultCard from "../components/ResultCard";

export default function Index() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [result, setResult] = useState<PlantAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function pickFromGallery() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Permission needed", "Gallery access is required to select a photo.");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    if (!result.canceled) {
      handleNewImage(result.assets[0].uri);
    }
  }

  async function takePhoto() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Permission needed", "Camera access is required to take a photo.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
    });

    if (!result.canceled) {
      handleNewImage(result.assets[0].uri);
    }
  }

  function handleNewImage(uri: string) {
    setImageUri(uri);
    setResult(null);
    setError(null);
  }

  async function analyzeImage() {
    if (!imageUri) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysis = await predictFull(imageUri);
      setResult(analysis);
    } catch (err) {
      console.error(err);
      setError(
        "Could not reach the analysis server. Check that your backend is running " +
          "and that BASE_URL in api/config.ts matches your computer's local IP."
      );
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setImageUri(null);
    setResult(null);
    setError(null);
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Plant Health Scanner</Text>
        <Text style={styles.subtitle}>
          Take or select a photo of a plant leaf to check for disease and severity.
        </Text>

        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.preview} />
        ) : (
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>No image selected</Text>
          </View>
        )}

        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={takePhoto}>
            <Text style={styles.buttonText}>Take Photo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={pickFromGallery}>
            <Text style={styles.buttonText}>Choose from Gallery</Text>
          </TouchableOpacity>
        </View>

        {imageUri && (
          <TouchableOpacity
            style={[styles.analyzeButton, loading && styles.analyzeButtonDisabled]}
            onPress={analyzeImage}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.analyzeButtonText}>Analyze Plant</Text>
            )}
          </TouchableOpacity>
        )}

        {error && <Text style={styles.errorText}>{error}</Text>}

        <ResultCard result={result} />

        {(imageUri || result) && (
          <TouchableOpacity style={styles.resetButton} onPress={reset}>
            <Text style={styles.resetButtonText}>Start Over</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F7F5",
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  title: {
    fontSize: 26,
    fontWeight: "700",
    color: "#1B4332",
    marginTop: 10,
  },
  subtitle: {
    fontSize: 14,
    color: "#555",
    marginTop: 6,
    marginBottom: 20,
  },
  preview: {
    width: "100%",
    height: 280,
    borderRadius: 12,
    marginBottom: 16,
  },
  placeholder: {
    width: "100%",
    height: 280,
    borderRadius: 12,
    backgroundColor: "#E0E5E0",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  placeholderText: {
    color: "#888",
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
  },
  button: {
    flex: 1,
    backgroundColor: "#2D6A4F",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 14,
  },
  analyzeButton: {
    marginTop: 16,
    backgroundColor: "#1B4332",
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: "center",
  },
  analyzeButtonDisabled: {
    opacity: 0.6,
  },
  analyzeButtonText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 16,
  },
  errorText: {
    color: "#D32F2F",
    marginTop: 14,
    fontSize: 13,
  },
  resetButton: {
    marginTop: 20,
    alignItems: "center",
  },
  resetButtonText: {
    color: "#666",
    textDecorationLine: "underline",
  },
});