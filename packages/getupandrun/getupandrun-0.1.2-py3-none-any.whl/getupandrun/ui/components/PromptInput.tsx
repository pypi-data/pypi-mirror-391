"use client";

import { useState } from "react";

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onNext?: () => void;
}

const EXAMPLE_PROMPTS = [
  "React frontend with Node.js backend and PostgreSQL database",
  "FastAPI Python backend with Redis cache",
  "Django web application with PostgreSQL database",
  "Vue.js frontend with Express backend and MongoDB",
  "Next.js application with PostgreSQL database",
];

export default function PromptInput({
  value,
  onChange,
  onNext,
}: PromptInputProps) {
  const [error, setError] = useState<string | null>(null);

  const validatePrompt = (prompt: string): { valid: boolean; error?: string } => {
    if (!prompt || prompt.trim().length === 0) {
      return { valid: false, error: "Prompt cannot be empty" };
    }
    if (prompt.trim().length < 10) {
      return { valid: false, error: "Prompt must be at least 10 characters" };
    }
    return { valid: true };
  };

  const handleChange = (newValue: string) => {
    onChange(newValue);
    const validation = validatePrompt(newValue);
    if (validation.valid) {
      setError(null);
    } else {
      setError(validation.error || null);
    }
  };

  const handleExampleClick = (example: string) => {
    handleChange(example);
  };

  const handleNext = () => {
    const validation = validatePrompt(value);
    if (validation.valid && onNext) {
      onNext();
    } else {
      setError(validation.error || "Please enter a valid prompt");
    }
  };

  const isValid = validatePrompt(value).valid;

  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="prompt"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Describe your project
        </label>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Tell us what you want to build in natural language
        </p>
        <textarea
          id="prompt"
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          rows={8}
          className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          placeholder="e.g., React frontend with Node.js backend and PostgreSQL database"
        />
        {error && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
        {!error && value && (
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {value.trim().length} characters
          </p>
        )}
      </div>

      <div>
        <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          Quick examples:
        </p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              className="rounded-md border border-gray-300 bg-white px-3 py-1 text-sm text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
            >
              {example.split(" ").slice(0, 3).join(" ")}...
            </button>
          ))}
        </div>
      </div>

      {onNext && (
        <div className="flex justify-end">
          <button
            onClick={handleNext}
            disabled={!isValid}
            className="rounded-md bg-indigo-600 px-6 py-2 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

