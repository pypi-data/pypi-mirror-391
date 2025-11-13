"use client";

export default function ProgressSpinner({ message }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
      {message && (
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">{message}</p>
      )}
    </div>
  );
}

