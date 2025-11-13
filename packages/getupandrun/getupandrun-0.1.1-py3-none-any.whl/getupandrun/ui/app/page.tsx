"use client";

import { useState } from "react";
import Link from "next/link";
import TemplateGrid from "../components/TemplateGrid";
import PromptInput from "../components/PromptInput";
import ProjectForm from "../components/ProjectForm";
import ProgressSpinner from "../components/ProgressSpinner";

type CreationMode = "choice" | "template" | "prompt" | "form" | "creating" | "success";

export default function Home() {
  const [mode, setMode] = useState<CreationMode>("choice");
  const [selectedTemplate, setSelectedTemplate] = useState<string | undefined>();
  const [prompt, setPrompt] = useState("");
  const [projectPath, setProjectPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTemplateSelect = (key: string) => {
    setSelectedTemplate(key);
    setMode("form");
  };

  const handlePromptNext = () => {
    setMode("form");
  };

  const handleProjectSubmit = async (data: {
    templateKey?: string;
    prompt?: string;
    projectName: string;
    baseDirectory: string;
  }) => {
    setMode("creating");
    setError(null);

    try {
      const response = await fetch("/api/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        // Show detailed error message if available
        const errorMessage = errorData.details 
          ? `${errorData.error}\n\n${errorData.details}${errorData.suggestion ? `\n\n${errorData.suggestion}` : ''}`
          : errorData.error || "Failed to create project";
        throw new Error(errorMessage);
      }

      // Check if it's a ZIP file (Vercel) or JSON response (local)
      const contentType = response.headers.get("content-type");
      if (contentType?.includes("application/zip")) {
        // Download ZIP file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${data.projectName}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setProjectPath(`Downloaded: ${data.projectName}.zip`);
      } else {
        // Local: get project path from JSON
        const result = await response.json();
        setProjectPath(result.projectPath || `Created at: ${data.baseDirectory}/${data.projectName}`);
      }

      setMode("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
      setMode("form");
    }
  };

  if (mode === "template") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <button
              onClick={() => setMode("choice")}
              className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
            >
              ← Back
            </button>
          </div>
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Select a Template
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Choose a predefined template to get started quickly
            </p>
          </div>
          <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
            <TemplateGrid
              onSelect={handleTemplateSelect}
              selectedKey={selectedTemplate}
            />
            {selectedTemplate && (
              <div className="mt-6 text-center">
                <button
                  onClick={() => setMode("form")}
                  className="rounded-md bg-indigo-600 px-6 py-2 text-white hover:bg-indigo-700"
                >
                  Continue to Project Form
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    );
  }

  if (mode === "prompt") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <button
              onClick={() => setMode("choice")}
              className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
            >
              ← Back
            </button>
          </div>
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Describe Your Project
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Tell us what you want to build in natural language
            </p>
          </div>
          <div className="mx-auto max-w-2xl rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              onNext={handlePromptNext}
            />
          </div>
        </main>
      </div>
    );
  }

  if (mode === "form") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <button
              onClick={() => {
                setMode(selectedTemplate ? "template" : "prompt");
                setError(null);
              }}
              className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
            >
              ← Back
            </button>
          </div>
          <div className="mx-auto max-w-2xl">
            <div className="mb-8 text-center">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                Project Details
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Configure your project settings
              </p>
            </div>
            <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
              {error && (
                <div className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900 dark:text-red-200">
                  <div className="whitespace-pre-line">{error}</div>
                </div>
              )}
              <ProjectForm
                templateKey={selectedTemplate}
                prompt={prompt}
                onSubmit={handleProjectSubmit}
                onCancel={() => {
                  setMode(selectedTemplate ? "template" : "prompt");
                  setError(null);
                }}
              />
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (mode === "creating") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="w-full max-w-2xl px-8">
          <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
            <ProgressSpinner message="Creating your project..." />
          </div>
        </main>
      </div>
    );
  }

  if (mode === "success") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="w-full max-w-2xl px-8">
          <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
                Project Created Successfully!
              </h2>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                {projectPath}
              </p>
              
              <div className="mt-6 rounded-lg bg-blue-50 p-6 dark:bg-blue-900/20">
                <h3 className="mb-3 text-lg font-semibold text-gray-900 dark:text-white">
                  Next Steps
                </h3>
                <ol className="space-y-2 text-left text-sm text-gray-700 dark:text-gray-300">
                  <li className="flex items-start">
                    <span className="mr-2 font-bold text-indigo-600 dark:text-indigo-400">1.</span>
                    <span>Start all services with automatic port conflict resolution:</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 font-bold text-indigo-600 dark:text-indigo-400">2.</span>
                    <span>Check service status with <code className="rounded bg-gray-100 px-2 py-1 font-mono text-xs dark:bg-gray-800">getupandrun status</code></span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 font-bold text-indigo-600 dark:text-indigo-400">3.</span>
                    <span>View logs with <code className="rounded bg-gray-100 px-2 py-1 font-mono text-xs dark:bg-gray-800">make logs</code> (from project directory)</span>
                  </li>
                </ol>
                <div className="mt-4 rounded-md bg-gray-900 p-4 dark:bg-black">
                  <code className="block text-left font-mono text-sm text-green-400">
                    <span className="text-gray-500 select-none">$ </span>getupandrun start {projectPath?.replace(/^Created at: /, "").replace(/^Downloaded: /, "").replace(/\.zip$/, "") || "your-project"}
                  </code>
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={() => {
                    setMode("choice");
                    setSelectedTemplate(undefined);
                    setPrompt("");
                    setProjectPath(null);
                    setError(null);
                  }}
                  className="rounded-md bg-indigo-600 px-6 py-2 text-white hover:bg-indigo-700"
                >
                  Create Another Project
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="w-full max-w-4xl px-8 py-16">
        <div className="space-y-8 text-center">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 dark:text-white">
              GetUpAndRun
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Scaffold development environments from natural language descriptions
            </p>
          </div>

          <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
            <h2 className="mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
              How would you like to create your project?
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              <button
                onClick={() => setMode("template")}
                className="rounded-lg border-2 border-gray-200 bg-white p-6 text-left transition-all hover:border-indigo-500 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Use a Template
                </h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Choose from predefined templates for common stacks
                </p>
              </button>
              <button
                onClick={() => setMode("prompt")}
                className="rounded-lg border-2 border-gray-200 bg-white p-6 text-left transition-all hover:border-indigo-500 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Custom Prompt
                </h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Describe your project in natural language
                </p>
              </button>
            </div>
          </div>

          <div className="text-center">
            <Link
              href="/settings"
              className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
            >
              Settings
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
