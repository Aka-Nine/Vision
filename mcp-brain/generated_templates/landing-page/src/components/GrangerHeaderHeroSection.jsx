import React from 'react';
import { motion } from 'framer-motion';

export default function GrangerHeaderHeroSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-white py-32 border-t border-b border-white/5 relative z-10">

        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="bg-gray-50 border border-gray-200 p-16 rounded-3xl">
            <span className="font-mono text-xs text-indigo-400 tracking-widest uppercase mb-4 block">Component / granger_header_hero</span>
            <h2 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6">
              Experience liftoff with the next-generation IDE
            </h2>

            <div className="flex gap-4 justify-center mt-8"><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">Download for Windows</button><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">Explore use cases</button></div>
          </div>
        </div>
      </section>
    </motion.div>
  );
}
