import React, { useRef, useEffect, useState } from "react";

export default function ThrobbingAudioCircle({ src }: { src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [intensity, setIntensity] = useState(0);

  useEffect(() => {
    if (!audioRef.current) return;
    const audio = audioRef.current;
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = ctx.createAnalyser();
    const source = ctx.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(ctx.destination);
    analyser.fftSize = 64;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    let running = true;
    function animate() {
      analyser.getByteFrequencyData(dataArray);
      const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setIntensity(avg / 255);
      if (running) requestAnimationFrame(animate);
    }
    animate();

    return () => {
      running = false;
      ctx.close();
    };
  }, [src]);

  const scale = 1 + intensity * 0.5;

  return (
    <div style={{ textAlign: "center", margin: "2rem 0" }}>
      <div
        style={{
          margin: "0 auto",
          width: 160,
          height: 160,
          borderRadius: "50%",
          background: "conic-gradient(from 0deg, #ffb300, #ff9100, #ffb300)",
          boxShadow: "0 0 40px 10px #ffb30088",
          transform: `scale(${scale})`,
          transition: "transform 0.1s linear",
          animation: "spin 2s linear infinite"
        }}
      />
      <audio ref={audioRef} src={src} autoPlay controls style={{ marginTop: 24, width: "100%" }} />
      <style>{`
        @keyframes spin {
          0% { filter: hue-rotate(0deg);}
          100% { filter: hue-rotate(360deg);}
        }
      `}</style>
    </div>
  );
} 