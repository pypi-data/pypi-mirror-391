/**
 * Project creation API route for GetUpAndRun UI.
 * Creates projects by calling the Python CLI via subprocess.
 */

import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { join } from "path";
import { homedir } from "os";
import { promises as fs } from "fs";
import archiver from "archiver";
import { createWriteStream } from "fs";

const execAsync = promisify(exec);

/**
 * Detect if running on Vercel
 */
function isVercel(): boolean {
  return !!process.env.VERCEL;
}

/**
 * Detect if running on Railway (or other platforms with Python)
 */
function hasPythonRuntime(): boolean {
  // Railway, Render, and other platforms that support Python
  // Check if we're NOT on Vercel (which doesn't have Python)
  return !process.env.VERCEL || !!process.env.RAILWAY_ENVIRONMENT;
}

/**
 * Expand ~ in path to home directory
 */
function expandPath(path: string): string {
  return path.replace(/^~/, homedir());
}

/**
 * Get the GetUpAndRun CLI command
 * Uses Python module execution for better compatibility, especially on Vercel
 */
function getCLICommand(): string {
  // Check for environment variable override
  const envCliPath = process.env.GETUPANDRUN_CLI_PATH;
  
  // Only use env var if it's explicitly set AND it's not just "getupandrun"
  // AND it includes python or is a full path (not just a command name)
  if (envCliPath && 
      envCliPath !== "getupandrun" &&
      (envCliPath.includes("python") || envCliPath.includes("/") || envCliPath.startsWith("python"))) {
    console.log(`Using GETUPANDRUN_CLI_PATH from env: ${envCliPath}`);
    return envCliPath;
  }
  
  // Always use Python module execution - more reliable than assuming getupandrun is in PATH
  // This works both locally (if installed via pip) and on Vercel
  const pythonPath = process.env.PYTHON_PATH || "python3";
  const command = `${pythonPath} -m getupandrun.cli.main`;
  
  // Log for debugging
  console.log(`CLI command constructed: ${command}`);
  console.log(`GETUPANDRUN_CLI_PATH env: ${envCliPath || "not set"}`);
  console.log(`PYTHON_PATH env: ${process.env.PYTHON_PATH || "not set (using python3)"}`);
  
  // Safety check: never return just "getupandrun"
  if (command === "getupandrun" || command.trim() === "getupandrun") {
    throw new Error("Invalid CLI command: getupandrun. Must use python3 -m getupandrun.cli.main");
  }
  
  return command;
}

/**
 * Create project locally by calling Python CLI
 */
async function createProjectLocal(
  templateKey: string | undefined,
  prompt: string | undefined,
  projectName: string,
  baseDirectory: string
): Promise<{ success: boolean; projectPath?: string; error?: string }> {
  try {
    const expandedBaseDir = expandPath(baseDirectory);
    const projectPath = join(expandedBaseDir, projectName);

    // Ensure base directory exists
    await fs.mkdir(expandedBaseDir, { recursive: true });

    // Change to base directory
    process.chdir(expandedBaseDir);

    // Build CLI command
    let command = getCLICommand();
    
    // Escape special characters in prompt/template
    if (templateKey) {
      command += ` --template ${templateKey}`;
    } else if (prompt) {
      // Escape quotes and special characters in prompt
      const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/\$/g, '\\$');
      command += ` --prompt "${escapedPrompt}"`;
    } else {
      return { success: false, error: "Either template or prompt must be provided" };
    }

    command += ` --name ${projectName}`;

    // Execute CLI command
    // Pass environment variables (including OPENAI_API_KEY) to subprocess
    console.log(`Executing command: ${command}`);
    console.log(`Working directory: ${expandedBaseDir}`);
    console.log(`Python path: ${process.env.PYTHON_PATH || "python3"}`);
    
    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: expandedBaseDir,
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer
        env: {
          ...process.env, // Inherit all environment variables including OPENAI_API_KEY
        },
      });
      
      if (stdout) {
        console.log("CLI stdout:", stdout);
      }

      if (stderr && !stderr.includes("warning")) {
        console.error("CLI stderr:", stderr);
      }
    } catch (error: any) {
      console.error("Command execution error:", error);
      // If Python module not found, provide helpful error
      if (error.message && error.message.includes("command not found")) {
        throw new Error(
          `Python or getupandrun module not found. ` +
          `Command attempted: ${command}. ` +
          `Make sure Python 3 and getupandrun are installed. ` +
          `On Vercel, ensure the build script installs Python and getupandrun.`
        );
      }
      throw error;
    }

    return { success: true, projectPath };
  } catch (error) {
    console.error("Error creating project:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Create project and return as ZIP (for Vercel)
 */
async function createProjectZip(
  templateKey: string | undefined,
  prompt: string | undefined,
  projectName: string
): Promise<{ success: boolean; zipPath?: string; error?: string }> {
  // For Vercel, we can't write to filesystem permanently
  // Instead, we'll create the project in a temp directory and zip it
  try {
    const tempDir = join("/tmp", `getupandrun-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });

    // Create project in temp directory
    process.chdir(tempDir);

    let command = getCLICommand();
    
    // Escape special characters in prompt/template
    if (templateKey) {
      command += ` --template ${templateKey}`;
    } else if (prompt) {
      // Escape quotes and special characters in prompt
      const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/\$/g, '\\$');
      command += ` --prompt "${escapedPrompt}"`;
    } else {
      return { success: false, error: "Either template or prompt must be provided" };
    }

    command += ` --name ${projectName}`;

    // Pass environment variables (including OPENAI_API_KEY) to subprocess
    console.log(`Executing command: ${command}`);
    console.log(`Working directory: ${tempDir}`);
    console.log(`Python path: ${process.env.PYTHON_PATH || "python3"}`);
    console.log(`Is Vercel: ${isVercel()}`);
    console.log(`OPENAI_API_KEY present: ${!!process.env.OPENAI_API_KEY}`);
    console.log(`RAILWAY_ENVIRONMENT: ${process.env.RAILWAY_ENVIRONMENT || "not set"}`);
    
    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: tempDir,
        maxBuffer: 10 * 1024 * 1024,
        env: {
          ...process.env, // Inherit all environment variables including OPENAI_API_KEY
        },
      });
      
      if (stdout) {
        console.log("CLI stdout:", stdout);
      }

      if (stderr && !stderr.includes("warning")) {
        console.error("CLI stderr:", stderr);
      }
    } catch (error: any) {
      console.error("Command execution error:", error);
      console.error("Error details:", {
        message: error.message,
        code: error.code,
        signal: error.signal,
        command: command,
        pythonPath: process.env.PYTHON_PATH || "python3",
        isVercel: isVercel(),
        hasOpenAIKey: !!process.env.OPENAI_API_KEY,
        stdout: error.stdout,
        stderr: error.stderr,
      });
      
      // Extract stderr and stdout for better error messages
      const stderr = error.stderr || "";
      const stdout = error.stdout || "";
      
      // If command not found, provide helpful error
      if (error.message && error.message.includes("command not found")) {
        // Check if it's trying to use getupandrun directly (which shouldn't happen)
        if (error.message.includes("getupandrun: command not found")) {
          throw new Error(
            `The code tried to use 'getupandrun' directly, which is not available. ` +
            `This should use 'python3 -m getupandrun.cli.main' instead. ` +
            `Check if GETUPANDRUN_CLI_PATH environment variable is incorrectly set to 'getupandrun'. ` +
            `Command attempted: ${command}`
          );
        }
        // Otherwise it's Python not found
        throw new Error(
          `Python not found. Command attempted: ${command}. ` +
          `Python may not be installed or available in the runtime environment. ` +
          `Check Railway deployment logs to see if Python installation succeeded.`
        );
      }
      
      // If Python module not found
      if (error.message && (error.message.includes("No module named") || stderr.includes("No module named"))) {
        throw new Error(
          `getupandrun Python module not installed. ` +
          `Command attempted: ${command}. ` +
          `The build script should install getupandrun via pip, but it may have failed. ` +
          `Check Railway build logs for pip installation errors. ` +
          `Error: ${stderr || error.message}`
        );
      }
      
      // Check for OPENAI_API_KEY issues (only if error message explicitly mentions it)
      // Don't check process.env.OPENAI_API_KEY here because Railway might set it differently
      if (stderr.includes("OPENAI_API_KEY") || stderr.includes("API key") || stderr.includes("OpenAI API key")) {
        throw new Error(
          `OpenAI API key not configured or invalid. ` +
          `Please verify OPENAI_API_KEY environment variable is set in Railway settings. ` +
          `Command attempted: ${command}. ` +
          `Error: ${stderr || error.message}`
        );
      }
      
      // Generic error with stderr/stdout for debugging
      const errorDetails = stderr || stdout || error.message;
      throw new Error(
        `Command failed: ${command}\n\n` +
        `Error: ${errorDetails}\n\n` +
        `Check Railway deployment logs for more details. ` +
        `Exit code: ${error.code || "unknown"}`
      );
    }

    // Create ZIP file
    const zipPath = join("/tmp", `${projectName}.zip`);
    const output = createWriteStream(zipPath);
    const archive = archiver("zip", { zlib: { level: 9 } });

    return new Promise((resolve) => {
      archive.pipe(output);
      archive.directory(join(tempDir, projectName), false);
      archive.finalize();

      output.on("close", () => {
        resolve({ success: true, zipPath });
      });

      archive.on("error", (err) => {
        resolve({ success: false, error: err.message });
      });
    });
  } catch (error) {
    console.error("Error creating project ZIP:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * POST /api/create - Create a new project
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { templateKey, prompt, projectName, baseDirectory } = body;

    if (!projectName || !projectName.trim()) {
      return NextResponse.json(
        { error: "Project name is required" },
        { status: 400 }
      );
    }

    if (!templateKey && !prompt) {
      return NextResponse.json(
        { error: "Either template or prompt must be provided" },
        { status: 400 }
      );
    }

    const vercel = isVercel();
    const hasPython = hasPythonRuntime();
    // Detect if we're on a deployed platform (not localhost)
    const isDeployed = vercel || !!process.env.RAILWAY_ENVIRONMENT || !!process.env.RENDER;

    // On platforms with Python (Railway, Render, etc.), we can create projects
    // On Vercel (without Python), we need to return an error
    if (vercel && !hasPython) {
      // Vercel without Python - return error
      return NextResponse.json(
        { 
          error: "Python is not available in Vercel's serverless runtime",
          details: "Vercel's Node.js serverless functions don't include Python. " +
                  "Please deploy to Railway, Render, or another platform that supports Python, " +
                  "or use the local version: run 'getupandrun ui' locally.",
        },
        { status: 503 }
      );
    }

    // On deployed platforms, always create ZIP; on local, create in filesystem
    if (isDeployed || !baseDirectory) {
      // Deployed platform: create ZIP and return download
      console.log("Creating project (ZIP mode for deployment)");
      const result = await createProjectZip(templateKey, prompt, projectName);
      if (!result.success) {
        console.error("Failed to create project ZIP:", result.error);
        return NextResponse.json(
          { 
            error: result.error || "Failed to create project",
            details: "Check deployment logs for more details."
          },
          { status: 500 }
        );
      }
      // Return ZIP file
      const zipData = await fs.readFile(result.zipPath!);
      return new NextResponse(zipData, {
        headers: {
          "Content-Type": "application/zip",
          "Content-Disposition": `attachment; filename="${projectName}.zip"`,
        },
      });
    } else {
      // Local: create project in filesystem
      const result = await createProjectLocal(
        templateKey,
        prompt,
        projectName,
        baseDirectory || join(homedir(), "getupandrun-projects")
      );

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || "Failed to create project" },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        projectPath: result.projectPath,
      });
    }
  } catch (error) {
    console.error("Error in create API:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

