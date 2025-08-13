import React, {useEffect, useState} from 'react';

interface TranscriptProps {
  videoId: string;
}

export default function Transcript({videoId}: TranscriptProps) {
  const [text, setText] = useState<string | null>(null);

  useEffect(() => {
    async function loadTranscript() {
      try {
        const res = await fetch(`/transcripts/${videoId}/clean.txt`);
        if (res.ok) {
          const t = await res.text();
          setText(t);
        }
      } catch (e) {
        // Ignore fetch errors; transcript may not exist
      }
    }
    loadTranscript();
  }, [videoId]);

  if (!text) {
    return null;
  }

  return (
    <details>
      <summary>Show transcript</summary>
      <pre>{text}</pre>
    </details>
  );
}
