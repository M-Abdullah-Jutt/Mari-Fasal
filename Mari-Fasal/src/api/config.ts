
export const BASE_URL: string = "http://192.168.10.9:8000"; // <-- YOUR COMPUTER'S LOCAL IP HERE

export const ENDPOINTS = {
  DISEASE: `${BASE_URL}/predict-disease`,
  SEVERITY: `${BASE_URL}/predict-severity`,
} as const;