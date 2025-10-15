import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60 seconds timeout for slower websites
});

export const analyzeUrl = async (url) => {
  try {
    // Ensure URL has protocol
    let formattedUrl = url;
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      formattedUrl = "https://" + url;
    }

    const response = await api.post("/analyze", { url: formattedUrl });

    // Transform backend response to frontend format
    const backendData = response.data;

    console.log("🔍 Backend Response:", backendData);
    console.log("🚨 CAPTCHA Detected:", backendData.captcha_detected);

    return {
      url: backendData.url,
      found: backendData.found,
      captcha_detected: backendData.captcha_detected || false,
      component_type: backendData.components?.[0]?.type || "unknown",
      description: backendData.ai_analysis || "No analysis available",
      html_snippet: backendData.components?.[0]?.html || null,
      details: {
        has_password_field:
          backendData.components?.some(
            (c) =>
              c.type.includes("password") ||
              c.html?.toLowerCase().includes("password")
          ) || false,
        has_email_field:
          backendData.components?.some((c) =>
            c.html?.toLowerCase().includes("email")
          ) || false,
        has_username_field:
          backendData.components?.some((c) =>
            c.html?.toLowerCase().includes("username")
          ) || false,
        has_submit_button:
          backendData.components?.some(
            (c) =>
              c.html?.toLowerCase().includes("submit") ||
              c.html?.toLowerCase().includes("button")
          ) || false,
      },
      confidence: backendData.found ? "high" : "low",
      analyzed_at: new Date().toLocaleString(),
      method: backendData.method || "static",
    };
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || "Failed to analyze URL");
    } else if (error.request) {
      throw new Error(
        "No response from server. Please check if the backend is running."
      );
    } else {
      throw new Error("Failed to send request");
    }
  }
};

export default api;
