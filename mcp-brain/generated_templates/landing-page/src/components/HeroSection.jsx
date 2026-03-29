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
      <section className="{cls['section']} py-32 text-center relative overflow-hidden min-h-screen flex items-center justify-center">
        <canvas ref={canvasRef} className="absolute inset-0 z-0 opacity-50 pointer-events-none" />
        <div className="absolute inset-0 {cls['bg_gradient']} z-0"></div>
        <div className="relative z-10 max-w-5xl mx-auto px-6">
          <h1 className="text-5xl md:text-8xl font-extrabold {cls['heading']} mb-6 leading-tight">
            Experience liftoff with the next-generation IDE
          </h1>
          <p className="{cls['subtext']} text-xl md:text-2xl max-w-3xl mx-auto mb-12">
            Transform your ideas into production-ready templates powered by market intelligence.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button className="{cls['btn_primary']} px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105 shadow-xl">
              Download for Windows
            </button>
            <button className="{cls['btn_secondary']} px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:scale-105 shadow-[0_0_15px_rgba(255,255,255,0.1)] backdrop-blur-md">
              Explore use cases
            </button>
          </div>
        </div>
      </section>
    </motion.div>
  );
}
