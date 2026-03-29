import React from 'react';
import { motion } from 'framer-motion';

export default function AboutSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-white py-32 border-t border-b border-white/5 relative z-10">

        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="bg-gray-50 border border-gray-200 p-16 rounded-3xl">
            <span className="font-mono text-xs text-indigo-400 tracking-widest uppercase mb-4 block">Component / about</span>
            <h2 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6">
              TurboQuant: Redefining AI efficiency with extreme compression
            </h2>


          </div>
        </div>
      </section>
    </motion.div>
  );
}
