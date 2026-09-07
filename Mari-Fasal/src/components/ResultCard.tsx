import React from "react";
import { View, Text, StyleSheet } from "react-native";
import type { CombinedResult } from "../api/plantApi";

interface ResultCardProps {
  result: CombinedResult | null;
}

/**
 * Formats a raw class name like "Tomato___Late_blight" into "Tomato - Late blight"
 */
function formatClassName(rawClass?: string): string {
  if (!rawClass) return "";
  return rawClass.replace(/___/g, " - ").replace(/_/g, " ");
}

function getSeverityLevel(pct: number): { label: string; color: string } {
  if (pct < 10) return { label: "Low", color: "#4CAF50" };
  if (pct < 30) return { label: "Moderate", color: "#FF9800" };
  return { label: "High", color: "#F44336" };
}

export default function ResultCard({ result }: ResultCardProps) {
  if (!result) return null;

  const isHealthy = result.class?.toLowerCase().includes("healthy");
  const severityPct = result.severity_percentage ?? 0;
  const severity = getSeverityLevel(severityPct);

  return (
    <View style={styles.card}>
      <Text style={styles.label}>Diagnosis</Text>
      <Text style={styles.diseaseName}>{formatClassName(result.class)}</Text>
      <Text style={styles.confidence}>
        Confidence: {result.confidence_percentage}
      </Text>

      {!isHealthy && (
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
          <Text style={styles.severityDetail}>
            {result.disease_pixels} affected pixels out of {result.plant_pixels} total plant pixels
          </Text>
        </View>
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
  severityDetail: {
    marginTop: 6,
    fontSize: 12,
    color: "#999",
  },
  healthyNote: {
    marginTop: 12,
    fontSize: 14,
    color: "#4CAF50",
    fontWeight: "500",
  },
});