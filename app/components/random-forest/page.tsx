'use client';

import { useState } from 'react';

export default function RandomForestPage() {
  const [file, setFile] = useState<File | null>(null);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a valid CSV file');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/fraud-detection', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process file');
      }

      const result = await response.json();
      setAccuracy(result.accuracy);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-md rounded-lg p-8 shadow-2xl">
        <h1 className="text-3xl font-bold text-white text-center mb-8">
          Fraud Detection with Random Forest
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Upload CSV File
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="w-full px-3 py-2 bg-white/20 border border-gray-300/30 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition duration-200 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Analyze Fraud Detection'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-500/20 border border-red-500/30 rounded-md">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {accuracy !== null && (
          <div className="mt-6 p-4 bg-green-500/20 border border-green-500/30 rounded-md">
            <h2 className="text-green-300 font-semibold mb-2">Analysis Complete</h2>
            <p className="text-white text-lg">
              Model Accuracy: <span className="font-bold text-green-300">{(accuracy * 100).toFixed(2)}%</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
