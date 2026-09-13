import React from "react";
import { View, Text, StyleSheet } from "react-native";
import type { PlantAnalysisResult } from "../api/plantApi";

interface ResultCardProps {
  result: PlantAnalysisResult | null;
}

function getSeverityLevel(pct: number): { label: string; color: string } {
  if (pct < 10) return { label: "Low", color: "#4CAF50" };
  if (pct < 30) return { label: "Moderate", color: "#FF9800" };
  return { label: "High", color: "#F44336" };
}

export default function ResultCard({ result }: ResultCardProps) {
  if (!result) return null;

  const isHealthy = result.disease_class?.toLowerCase().includes("healthy");
  const severityPct = result.severity_percentage ?? 0;
  const severity = getSeverityLevel(severityPct);

  return (
    <View style={styles.card}>
      <Text style={styles.label}>Crop</Text>
      <Text style={styles.cropName}>{result.crop ?? "Unknown"}</Text>

      <Text style={[styles.label, styles.sectionSpacing]}>Diagnosis</Text>
      <Text style={styles.diseaseName}>{result.disease_name ?? result.disease_class}</Text>
      <Text style={styles.confidence}>
        Confidence: {result.disease_confidence.toFixed(2)}%
      </Text>

      {!isHealthy && (
        <>
          <View style={styles.severitySection}>
            <Text style={styles.label}>Severity</Text>
            <View style={styles.severityRow}>
              <Text style={[styles.severityValue, { color: severity.color }]}>
                {severityPct.toFixed(1)}%
              </Text>
              <View style={[styles.badge, { backgroundColor: severity.color }]}>
                <Text style={styles.badgeText}>{severity.label}</Text>
              </View>
            </View>
          </View>

          {result.causes.length > 0 && (
            <View style={styles.infoSection}>
              <Text style={styles.label}>Causes</Text>
              {result.causes.map((cause, idx) => (
                <Text key={idx} style={styles.bodyText}>
                  • {cause}
                </Text>
              ))}
            </View>
          )}

          {result.recommendations.length > 0 && (
            <View style={styles.infoSection}>
              <Text style={styles.label}>Recommendations</Text>
              {result.recommendations.map((rec, idx) => (
                <Text key={idx} style={styles.bodyText}>
                  • {rec}
                </Text>
              ))}
            </View>
          )}
        </>
      )}

      {isHealthy && (
        <Text style={styles.healthyNote}>
          No disease detected - this plant looks healthy.
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 20,
    marginTop: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 13,
    color: "#888",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  sectionSpacing: {
    marginTop: 14,
  },
  cropName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#2D6A4F",
  },
  diseaseName: {
    fontSize: 22,
    fontWeight: "700",
    color: "#222",
    marginBottom: 4,
  },
  confidence: {
    fontSize: 14,
    color: "#555",
  },
  severitySection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#eee",
  },
  severityRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  severityValue: {
    fontSize: 26,
    fontWeight: "700",
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "600",
  },
  infoSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#eee",
  },
  bodyText: {
    fontSize: 14,
    color: "#444",
    lineHeight: 20,
    marginTop: 6,
  },
  healthyNote: {
    marginTop: 12,
    fontSize: 14,
    color: "#4CAF50",
    fontWeight: "500",
  },
});