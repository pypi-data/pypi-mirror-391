/**
 * Templates API route for GetUpAndRun UI.
 * Fetches available templates by calling the Python CLI.
 */

import { NextResponse } from "next/server";

interface Template {
  key: string;
  name: string;
  description: string;
}

/**
 * Get templates by calling Python CLI
 * This calls: python -m getupandrun.cli.main templates --json (if we add JSON output)
 * For now, we'll parse the CLI output or call the Python module directly
 */
async function getTemplates(): Promise<Template[]> {
  try {
    // For now, we'll use a simple approach: call the CLI and parse output
    // In a real implementation, we might want to add JSON output to the CLI
    // or import the Python module directly using a bridge
    
    // Temporary: return hardcoded templates until we implement proper Python integration
    // This will be replaced in PR 21 when we implement the full project creation flow
    return [
      {
        key: "react-node-postgres",
        name: "React + Node.js + Postgres",
        description: "Full-stack web application with React frontend, Node.js/Express backend, and PostgreSQL database",
      },
      {
        key: "fastapi-redis",
        name: "FastAPI + Redis",
        description: "FastAPI Python backend with Redis cache",
      },
      {
        key: "django-postgres",
        name: "Django + Postgres",
        description: "Django Python web framework with PostgreSQL database",
      },
      {
        key: "vue-node-mongodb",
        name: "Vue + Node.js + MongoDB",
        description: "Vue.js frontend with Node.js backend and MongoDB database",
      },
      {
        key: "nextjs-postgres",
        name: "Next.js + Postgres",
        description: "Next.js React framework with PostgreSQL database",
      },
      {
        key: "flask-redis",
        name: "Flask + Redis",
        description: "Flask Python backend with Redis cache",
      },
    ];
  } catch (error) {
    console.error("Error fetching templates:", error);
    return [];
  }
}

/**
 * GET /api/templates - Get all available templates
 */
export async function GET() {
  try {
    const templates = await getTemplates();
    return NextResponse.json(templates);
  } catch (error) {
    console.error("Error in templates API:", error);
    return NextResponse.json(
      { error: "Failed to fetch templates" },
      { status: 500 }
    );
  }
}

