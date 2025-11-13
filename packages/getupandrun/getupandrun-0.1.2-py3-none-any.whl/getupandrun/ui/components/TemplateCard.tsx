"use client";

interface Template {
  key: string;
  name: string;
  description: string;
}

interface TemplateCardProps {
  template: Template;
  selected: boolean;
  onSelect: (key: string) => void;
}

export default function TemplateCard({
  template,
  selected,
  onSelect,
}: TemplateCardProps) {
  return (
    <button
      onClick={() => onSelect(template.key)}
      className={`w-full rounded-lg border-2 p-6 text-left transition-all hover:shadow-lg ${
        selected
          ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20"
          : "border-gray-200 bg-white hover:border-indigo-300 dark:border-gray-700 dark:bg-gray-800"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {template.name}
          </h3>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {template.description}
          </p>
        </div>
        {selected && (
          <div className="ml-4 flex-shrink-0">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-500">
              <svg
                className="h-4 w-4 text-white"
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
          </div>
        )}
      </div>
    </button>
  );
}

