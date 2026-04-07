import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function SCR15_BylawsUpload() {
  const location = useLocation();
  const navigate = useNavigate();

  const { society_id } = location.state || {};

  const [file, setFile] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("society_id", society_id);
    formData.append("file", file);

    try {
      setLoading(true);

      const res = await fetch(
        "http://127.0.0.1:8000/api/society/bylaws/upload/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      alert("Upload successful");

      navigate("/dashboard");

    } catch (err) {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 30 }}>
      <h2>Upload Signed By-laws</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(e: any) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Signed Copy"}
      </button>
    </div>
  );
}