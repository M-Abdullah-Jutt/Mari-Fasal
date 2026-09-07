import * as FileSystem from "expo-file-system/legacy";
import { ENDPOINTS } from "./config";

export interface DiseaseResult {
  class: string;
  confidence_raw: number;
  confidence_percentage: string;
}

export interface SeverityResult {
  severity_percentage: number;
  plant_pixels: number;
  disease_pixels: number;
}

export type CombinedResult = DiseaseResult & SeverityResult;

/**
 * Uploads an image file to a backend endpoint using expo-file-system's
 * uploadAsync, which handles multipart form uploads reliably across RN/Expo
 * versions.
 *
 * NOTE: We deliberately use `expo-file-system/legacy` here, not the
 * top-level `expo-file-system` import. As of expo-file-system v57+, the
 * top-level `uploadAsync` is kept only for type-compatibility and throws
 * at runtime - the working implementation now lives under `/legacy`.
 */
async function postImage<T>(url: string, imageUri: string): Promise<T> {
  const result = await FileSystem.uploadAsync(url, imageUri, {
    httpMethod: "POST",
    uploadType: FileSystem.FileSystemUploadType.MULTIPART,
    fieldName: "file",
  });

  if (result.status < 200 || result.status >= 300) {
    throw new Error(`Request failed (${result.status}): ${result.body}`);
  }

  return JSON.parse(result.body) as T;
}

/**
 * Sends the image to the disease classification endpoint.
 */
export async function predictDisease(imageUri: string): Promise<DiseaseResult> {
  return postImage<DiseaseResult>(ENDPOINTS.DISEASE, imageUri);
}

/**
 * Sends the image to the severity estimation endpoint.
 */
export async function predictSeverity(imageUri: string): Promise<SeverityResult> {
  return postImage<SeverityResult>(ENDPOINTS.SEVERITY, imageUri);
}

/**
 * Runs both predictions and combines the results into one object.
 * Uses Promise.all so both requests run concurrently rather than
 * waiting for one to finish before starting the other.
 */
export async function predictDiseaseAndSeverity(imageUri: string): Promise<CombinedResult> {
  const [diseaseResult, severityResult] = await Promise.all([
    predictDisease(imageUri),
    predictSeverity(imageUri),
  ]);

  return {
    ...diseaseResult,
    ...severityResult,
  };
}