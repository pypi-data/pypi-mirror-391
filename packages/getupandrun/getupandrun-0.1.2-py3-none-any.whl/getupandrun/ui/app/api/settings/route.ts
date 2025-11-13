/**
 * Settings API route for GetUpAndRun UI.
 * Handles CRUD operations for UI settings stored in ~/.getupandrun/ui-config.json
 */

import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import { join } from "path";
import { homedir } from "os";

const CONFIG_DIR = join(homedir(), ".getupandrun");
const CONFIG_FILE = join(CONFIG_DIR, "ui-config.json");
const DEFAULT_BASE_DIRECTORY = join(homedir(), "getupandrun-projects");

interface UISettings {
  baseDirectory: string;
}

const DEFAULT_SETTINGS: UISettings = {
  baseDirectory: DEFAULT_BASE_DIRECTORY,
};

/**
 * Detect if running on Vercel
 */
function isVercel(): boolean {
  return !!process.env.VERCEL;
}

/**
 * Expand ~ in path to home directory
 */
function expandPath(path: string): string {
  return path.replace(/^~/, homedir());
}

/**
 * Validate a path exists and is writable
 */
async function validatePath(path: string): Promise<{ valid: boolean; error?: string }> {
  if (!path || path.trim().length === 0) {
    return { valid: false, error: "Path cannot be empty" };
  }

  const expandedPath = expandPath(path);

  // Check if path is absolute
  if (!expandedPath.startsWith("/")) {
    return { valid: false, error: "Path must be absolute" };
  }

  try {
    // Check if path exists
    await fs.access(expandedPath);
    
    // Try to write a test file to check writability
    const testFile = join(expandedPath, ".getupandrun-test");
    try {
      await fs.writeFile(testFile, "test");
      await fs.unlink(testFile);
    } catch {
      return { valid: false, error: "Path is not writable" };
    }

    return { valid: true };
  } catch {
    // Path doesn't exist, try to create it
    try {
      await fs.mkdir(expandedPath, { recursive: true });
      return { valid: true };
    } catch (error) {
      return { valid: false, error: `Cannot create directory: ${error}` };
    }
  }
}

/**
 * Read settings from config file
 */
async function readSettings(): Promise<UISettings> {
  try {
    await fs.access(CONFIG_FILE);
    const content = await fs.readFile(CONFIG_FILE, "utf-8");
    const settings = JSON.parse(content) as UISettings;
    return settings;
  } catch {
    // File doesn't exist, return defaults
    return { ...DEFAULT_SETTINGS };
  }
}

/**
 * Write settings to config file
 */
async function writeSettings(settings: UISettings): Promise<void> {
  // Ensure config directory exists
  await fs.mkdir(CONFIG_DIR, { recursive: true });
  
  // Validate the base directory before saving
  const validation = await validatePath(settings.baseDirectory);
  if (!validation.valid) {
    throw new Error(validation.error || "Invalid path");
  }

  // Write settings to file
  await fs.writeFile(CONFIG_FILE, JSON.stringify(settings, null, 2), "utf-8");
}

/**
 * GET /api/settings - Get current settings
 */
export async function GET() {
  try {
    // On Vercel, settings are stored in browser localStorage, not server
    // Return a message indicating this
    if (isVercel()) {
      return NextResponse.json({
        baseDirectory: "~/getupandrun-projects/",
        message: "On Vercel, settings are stored in your browser. Projects are downloaded as ZIP files.",
        isVercel: true,
      });
    }
    
    const settings = await readSettings();
    return NextResponse.json(settings);
  } catch (error) {
    console.error("Error reading settings:", error);
    return NextResponse.json(
      { error: "Failed to read settings" },
      { status: 500 }
    );
  }
}

/**
 * POST /api/settings - Save settings
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // On Vercel, don't try to save to filesystem
    // Settings are stored in browser localStorage instead
    if (isVercel()) {
      return NextResponse.json({
        baseDirectory: body.baseDirectory || "~/getupandrun-projects/",
        message: "Settings saved to browser storage. Projects will be downloaded as ZIP files.",
        isVercel: true,
      });
    }
    
    // Local: save to filesystem as before
    const settings: UISettings = {
      baseDirectory: body.baseDirectory || DEFAULT_BASE_DIRECTORY,
    };

    // Validate path
    const validation = await validatePath(settings.baseDirectory);
    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.error || "Invalid path" },
        { status: 400 }
      );
    }

    await writeSettings(settings);
    return NextResponse.json(settings);
  } catch (error) {
    console.error("Error saving settings:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to save settings" },
      { status: 500 }
    );
  }
}

