import * as FileSystem from "expo-file-system/legacy";
import { ENDPOINTS } from "./config";

export interface PlantAnalysisResult {
  disease_class: string;
  disease_confidence: number;
  severity_percentage: number;
  crop: string | null;
  disease_name: string | null;
  causes: string[];
  recommendations: string[];
}

/**
 * Uploads an image to the combined /predict-full endpoint, which runs
 * disease classification, severity estimation, and the causes/recommendations
 * database lookup in one backend call.
 *
 * NOTE: We use `expo-file-system/legacy`, not the top-level `expo-file-system`
 * import. As of expo-file-system v57+, the top-level `uploadAsync` is kept
 * only for type-compatibility and throws at runtime - the working
 * implementation now lives under `/legacy`.
 */
export async function predictFull(imageUri: string): Promise<PlantAnalysisResult> {
  const result = await FileSystem.uploadAsync(ENDPOINTS.FULL, imageUri, {
    httpMethod: "POST",
    uploadType: FileSystem.FileSystemUploadType.MULTIPART,
    fieldName: "file",
  });

  if (result.status < 200 || result.status >= 300) {
    throw new Error(`Request failed (${result.status}): ${result.body}`);
  }

  return JSON.parse(result.body) as PlantAnalysisResult;
}