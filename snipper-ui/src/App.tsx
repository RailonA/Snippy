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

  const handleUpload = async () => {
    if (!file) return alert("Select a video first.");

    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(
      "http://127.0.0.1:8000/upload",
      formData
    );

    setJobId(response.data.job_id);
  };

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      const res = await axios.get(
        `http://127.0.0.1:8000/status/${jobId}`
      );

      setProgress(res.data.progress);

      if (res.data.status === "complete") {
        setClips(res.data.clips);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  const sortedClips = sortByScore
    ? [...clips].sort((a, b) => b.score - a.score)
    : clips;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-10">
      <h1 className="text-3xl font-bold mb-6">
        🎙️ Snipper Pro
      </h1>

      {/* Drag & Drop */}
      <div
        className="border-2 border-dashed border-gray-600 p-10 rounded-xl text-center mb-6 cursor-pointer hover:border-blue-500 transition"
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

      <button
        onClick={handleUpload}
        className="bg-blue-600 px-6 py-2 rounded mb-6"
      >
        Generate Clips
      </button>

      {/* Progress Bar */}
      {progress > 0 && progress < 100 && (
        <div className="w-full bg-gray-700 rounded-full h-4 mb-6">
          <div
            className="bg-blue-500 h-4 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {/* Settings */}
      <div className="mb-6">
        <label className="mr-3">Sort by Score</label>
        <input
          type="checkbox"
          checked={sortByScore}
          onChange={() => setSortByScore(!sortByScore)}
        />
      </div>

      {/* Clips */}
      <div className="grid md:grid-cols-2 gap-6">
        {sortedClips.map((clip, i) => (
          <div
            key={i}
            className="bg-gray-800 p-4 rounded-xl"
          >
            <h2 className="font-semibold mb-2">
              Score: {clip.score}
            </h2>

            <p className="text-sm text-gray-400 mb-3">
              {clip.text}
            </p>

            <video
              controls
              className="w-full rounded"
              src={`http://127.0.0.1:8000/output/clips/clip_${i+1}.mp4`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;