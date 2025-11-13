/**
 * Settings management utility for GetUpAndRun UI.
 * Handles reading and writing settings to ~/.getupandrun/ui-config.json
 */

export interface UISettings {
  baseDirectory: string;
}

const DEFAULT_BASE_DIRECTORY = "~/getupandrun-projects/";
const DEFAULT_SETTINGS: UISettings = {
  baseDirectory: DEFAULT_BASE_DIRECTORY,
};

/**
 * Detect if running on Vercel (client-side)
 */
function isVercel(): boolean {
  if (typeof window === "undefined") return false;
  return window.location.hostname.includes("vercel.app") || 
         window.location.hostname.includes("vercel.com");
}

/**
 * Get the default settings
 */
export function getDefaultSettings(): UISettings {
  return { ...DEFAULT_SETTINGS };
}

/**
 * Get settings from localStorage (Vercel) or API (local)
 */
export async function getSettings(): Promise<UISettings> {
  // On Vercel, use localStorage
  if (isVercel() && typeof window !== "undefined") {
    const stored = localStorage.getItem("getupandrun-settings");
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        // Invalid JSON, return defaults
      }
    }
    return getDefaultSettings();
  }
  
  // Local: fetch from API
  try {
    const response = await fetch("/api/settings");
    if (!response.ok) {
      // If settings don't exist, return defaults
      return getDefaultSettings();
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch settings:", error);
    return getDefaultSettings();
  }
}

/**
 * Save settings to localStorage (Vercel) or API (local)
 */
export async function saveSettings(settings: UISettings): Promise<boolean> {
  // On Vercel, use localStorage
  if (isVercel() && typeof window !== "undefined") {
    try {
      localStorage.setItem("getupandrun-settings", JSON.stringify(settings));
      return true;
    } catch (error) {
      console.error("Failed to save to localStorage:", error);
      return false;
    }
  }
  
  // Local: save via API
  try {
    const response = await fetch("/api/settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings),
    });
    return response.ok;
  } catch (error) {
    console.error("Failed to save settings:", error);
    return false;
  }
}

/**
 * Check if running on Vercel (exported for use in components)
 */
export function checkIsVercel(): boolean {
  return isVercel();
}

/**
 * Basic client-side path validation (server does full validation)
 */
export function validatePath(path: string): { valid: boolean; error?: string } {
  if (!path || path.trim().length === 0) {
    return { valid: false, error: "Path cannot be empty" };
  }

  // Basic check - paths should start with / or ~
  if (!path.startsWith("/") && !path.startsWith("~")) {
    return { valid: false, error: "Path must be absolute (start with / or ~)" };
  }

  return { valid: true };
}

