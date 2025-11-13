"use client";

import { useState, useEffect } from "react";
import { getSettings, checkIsVercel } from "../utils/settings";

interface ProjectFormProps {
  templateKey?: string;
  prompt?: string;
  onSubmit: (data: {
    templateKey?: string;
    prompt?: string;
    projectName: string;
    baseDirectory: string;
  }) => void;
  onCancel: () => void;
}

export default function ProjectForm({
  templateKey,
  prompt,
  onSubmit,
  onCancel,
}: ProjectFormProps) {
  const [projectName, setProjectName] = useState("");
  const [baseDirectory, setBaseDirectory] = useState("");
  const [loading, setLoading] = useState(true);
  const [isVercel, setIsVercel] = useState(false);

  useEffect(() => {
    setIsVercel(checkIsVercel());
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const settings = await getSettings();
      setBaseDirectory(settings.baseDirectory);
    } catch {
      setBaseDirectory("~/getupandrun-projects/");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim()) {
      return;
    }
    onSubmit({
      templateKey,
      prompt,
      projectName: projectName.trim(),
      baseDirectory,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-lg text-gray-600 dark:text-gray-400">
          Loading...
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label
          htmlFor="projectName"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Project Name
        </label>
        <input
          type="text"
          id="projectName"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          required
          className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          placeholder="my-awesome-project"
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          This will be the name of your project directory
        </p>
      </div>

      {isVercel ? (
        <div className="rounded-md bg-blue-50 p-4 dark:bg-blue-900/20">
          <p className="text-sm font-semibold text-blue-800 dark:text-blue-200">
            📦 Project Download
          </p>
          <p className="mt-1 text-sm text-blue-700 dark:text-blue-300">
            Your project will be downloaded as a ZIP file. Extract it to your desired location on your computer.
          </p>
        </div>
      ) : (
        <div>
          <label
            htmlFor="baseDirectory"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Base Directory
          </label>
          <input
            type="text"
            id="baseDirectory"
            value={baseDirectory}
            readOnly
            className="mt-2 block w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 shadow-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Project will be created at: {baseDirectory}
            {projectName && `/${projectName}`}
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            <a href="/settings" className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
              Change in settings
            </a>
          </p>
        </div>
      )}

      {(templateKey || prompt) && (
        <div className="rounded-md bg-blue-50 p-4 dark:bg-blue-900/20">
          <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
            {templateKey ? "Using template:" : "Using prompt:"}
          </p>
          <p className="mt-1 text-sm text-blue-700 dark:text-blue-300">
            {templateKey || prompt}
          </p>
        </div>
      )}

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={!projectName.trim()}
          className="rounded-md bg-indigo-600 px-6 py-2 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Create Project
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 px-6 py-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

