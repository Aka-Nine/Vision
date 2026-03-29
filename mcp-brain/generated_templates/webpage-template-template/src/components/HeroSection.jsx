import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export default function HeroSection() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, particles = [];
    const resize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
    window.addEventListener('resize', resize);
    resize();

    for(let i=0; i<50; i++) particles.push({x: Math.random()*w, y: Math.random()*h, v: Math.random()*0.5});

    const draw = () => {
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      particles.forEach(p => {
        p.y -= p.v; if (p.y < 0) p.y = h;
        ctx.beginPath(); ctx.arc(p.x, p.y, 1.5, 0, Math.PI*2); ctx.fill();
      });
      requestAnimationFrame(draw);
    };
    draw();
    return () => window.removeEventListener('resize', resize);
  }, []);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-gray-950 py-32 text-center relative overflow-hidden">
        <canvas ref={canvasRef} className="absolute inset-0 z-0 opacity-50 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/40 via-purple-900/20 to-transparent z-0"></div>
        <div className="relative z-10 max-w-5xl mx-auto px-6">
          <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight">
            Build AI Products Faster
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-10">
            Transform your ideas into production-ready templates powered by market intelligence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105">
              Get Started
            </button>
            <button className="bg-white/10 hover:bg-white/20 text-white border border-white/10 px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105 shadow-[0_0_15px_rgba(255,255,255,0.1)] backdrop-blur-md">
              View Demo
            </button>
          </div>
        </div>
      </section>
    </motion.div>
  );
}
