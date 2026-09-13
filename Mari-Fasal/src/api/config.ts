
export const BASE_URL: string = "http://192.168.10.19:8000"; // <-- YOUR COMPUTER'S LOCAL IP + PORT
 
export const ENDPOINTS = {
  FULL: `${BASE_URL}/predict-full`,
} as const;
 