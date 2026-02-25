import { useState, useEffect } from "react";
import axios from "axios";

interface Clip {
  file: string;
  score: number;
  text: string;
  start: number;
  end: number;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [clips, setClips] = useState<Clip[]>([]);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [sortByScore, setSortByScore] = useState(true);
  const [keywordsInput, setKeywordsInput] = useState<string>("");

  // Handle upload
  const handleUpload = async () => {
    if (!file) return alert("Select a video first.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      );
      setJobId(response.data.job_id);
      setProgress(0);
    } catch {
      alert("Upload failed. Is backend running?");
    }
  };

  // Poll backend for job progress
  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(
          `http://127.0.0.1:8000/status/${jobId}`
        );
        setProgress(res.data.progress || 0);

        if (res.data.status === "complete") {
          setClips(res.data.clips);
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  // Update keywords in config.yaml
  const updateKeywords = async () => {
    const keywords = keywordsInput
      .split(",")
      .map((k) => k.trim())
      .filter(Boolean);

    if (!keywords.length) return alert("Enter at least one keyword.");

    try {
      await axios.post("http://127.0.0.1:8000/update-keywords", keywords);
      alert("Keywords updated!");
    } catch {
      alert("Failed to update keywords.");
    }
  };

  // Sort clips
  const sortedClips = sortByScore
    ? [...clips].sort((a, b) => b.score - a.score)
    : clips;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-10">
      <h1 className="text-4xl font-bold mb-8 text-center">
        🎙️ Snipper Dashboard
      </h1>

      {/* Upload Section */}
      <div
        className="border-2 border-dashed border-gray-600 p-10 rounded-xl text-center mb-6 cursor-pointer hover:border-blue-500 transition max-w-xl mx-auto"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => document.getElementById("fileInput")?.click()}
      >
        {file ? (
          <p className="text-blue-400 font-semibold">{file.name}</p>
        ) : (
          <p className="text-gray-400">Drag & Drop Podcast Here or Click</p>
        )}

        <input
          id="fileInput"
          type="file"
          accept="video/mp4"
          className="hidden"
          onChange={(e) =>
            setFile(e.target.files ? e.target.files[0] : null)
          }
        />
      </div>

      {/* Keywords Input */}
      <div className="bg-gray-800 p-4 rounded-xl mb-6 max-w-xl mx-auto w-full">
        <h2 className="font-semibold mb-2 text-white">Update Keywords</h2>
        <input
          type="text"
          value={keywordsInput}
          onChange={(e) => setKeywordsInput(e.target.value)}
          placeholder="Enter keywords, separated by commas"
          className="w-full p-2 rounded mb-2 text-black bg-white border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        <button
          onClick={updateKeywords}
          className="bg-green-600 px-4 py-2 rounded hover:bg-green-500 text-white"
        >
          Save Keywords
        </button>
      </div>

      <button
        onClick={handleUpload}
        className="bg-blue-600 px-6 py-2 rounded mb-6 w-full max-w-xl block mx-auto hover:bg-blue-500"
      >
        Generate Clips
      </button>

      {/* Progress Bar */}
      {progress > 0 && progress < 100 && (
        <div className="w-full max-w-xl bg-gray-700 rounded-full h-4 mb-6 mx-auto">
          <div
            className="bg-blue-500 h-4 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {/* Sorting Toggle */}
      <div className="flex justify-center items-center mb-6">
        <label className="mr-2">Sort clips by score</label>
        <input
          type="checkbox"
          checked={sortByScore}
          onChange={() => setSortByScore(!sortByScore)}
        />
      </div>

      {/* Clips Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {sortedClips.map((clip, i) => (
          <div
            key={i}
            className="bg-gray-800 p-4 rounded-xl shadow-lg"
          >
            <h2 className="font-semibold mb-2">
              Score: {clip.score} — Clip {i + 1}
            </h2>

            <p className="text-sm text-gray-400 mb-3">{clip.text}</p>

            <video
              controls
              className="w-full rounded"
              src={`http://127.0.0.1:8000/output/clips/clip_${i + 1}.mp4`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;