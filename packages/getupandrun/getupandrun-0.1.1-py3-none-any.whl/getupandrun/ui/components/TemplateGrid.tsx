"use client";

import { useState, useEffect } from "react";
import TemplateCard from "./TemplateCard";

interface Template {
  key: string;
  name: string;
  description: string;
}

interface TemplateGridProps {
  onSelect: (key: string) => void;
  selectedKey?: string;
}

export default function TemplateGrid({
  onSelect,
  selectedKey,
}: TemplateGridProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/templates");
      if (!response.ok) {
        throw new Error("Failed to fetch templates");
      }
      const data = await response.json();
      setTemplates(data);
    } catch (err) {
      setError("Failed to load templates");
      console.error("Error fetching templates:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-gray-600 dark:text-gray-400">
          Loading templates...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900 dark:text-red-200">
        {error}
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="rounded-md bg-yellow-50 p-4 text-sm text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
        No templates available.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {templates.map((template) => (
        <TemplateCard
          key={template.key}
          template={template}
          selected={selectedKey === template.key}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

