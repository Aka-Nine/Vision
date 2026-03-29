import React from 'react';
import { motion } from 'framer-motion';

export default function VideoSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-white py-32 border-t border-b border-white/5 relative z-10">

        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-3xl md:text-5xl font-bold text-gray-900 text-center mb-10">TurboQuant: Redefining AI efficiency with extreme compression</h2>

          <div className="aspect-video bg-black rounded-2xl flex border border-gray-200 items-center justify-center shadow-2xl overflow-hidden relative group cursor-pointer mt-8">
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
            <div className="w-24 h-24 rounded-full bg-indigo-600/90 flex items-center justify-center transition-transform group-hover:scale-110 z-10 backdrop-blur-md">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
            </div>
          </div>
          <div className="flex gap-4 justify-center mt-8"><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">close</button></div>
        </div>
      </section>
    </motion.div>
  );
}
