"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getSettings, saveSettings, validatePath, getDefaultSettings, checkIsVercel } from "../../utils/settings";

export default function SettingsPage() {
  const [baseDirectory, setBaseDirectory] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isVercel, setIsVercel] = useState(false);

  useEffect(() => {
    setIsVercel(checkIsVercel());
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const settings = await getSettings();
      setBaseDirectory(settings.baseDirectory);
    } catch {
      setError("Failed to load settings");
      const defaults = getDefaultSettings();
      setBaseDirectory(defaults.baseDirectory);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setError(null);
    setSuccess(false);

    // On Vercel, just check that it's not empty (we can't validate paths)
    // Locally, do full validation
    if (!isVercel) {
      const validation = validatePath(baseDirectory);
      if (!validation.valid) {
        setError(validation.error || "Invalid path");
        return;
      }
    } else {
      // On Vercel, just check it's not empty
      if (!baseDirectory || baseDirectory.trim().length === 0) {
        setError("Path cannot be empty");
        return;
      }
    }

    setSaving(true);
    try {
      const saved = await saveSettings({ baseDirectory });
      if (saved) {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError("Failed to save settings");
      }
    } catch {
      setError("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    const defaults = getDefaultSettings();
    setBaseDirectory(defaults.baseDirectory);
    setError(null);
    setSuccess(false);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg text-gray-600 dark:text-gray-400">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="w-full max-w-2xl p-8">
        <div className="rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
          <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-white">
            Settings
          </h1>

          <div className="space-y-6">
            <div>
              <label
                htmlFor="baseDirectory"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Base Directory
              </label>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Where new projects will be created. Use ~ for home directory.
              </p>
              <input
                type="text"
                id="baseDirectory"
                value={baseDirectory}
                onChange={(e) => setBaseDirectory(e.target.value)}
                className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="~/getupandrun-projects/"
              />
              {isVercel && (
                <div className="mt-3 rounded-md bg-blue-50 p-3 text-sm text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  <p className="font-semibold">ℹ️ Deployed Version</p>
                  <p className="mt-1">
                    Settings are stored in your browser. Projects will be downloaded as ZIP files 
                    since we cannot access your local file system.
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900 dark:text-red-200">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-md bg-green-50 p-4 text-sm text-green-800 dark:bg-green-900 dark:text-green-200">
                Settings saved successfully!
              </div>
            )}

            <div className="flex gap-4">
              <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Settings"}
              </button>
              <button
                onClick={handleReset}
                className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Reset to Defaults
              </button>
              <Link
                href="/"
                className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

