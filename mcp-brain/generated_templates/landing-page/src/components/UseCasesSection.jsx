import React from 'react';
import { motion } from 'framer-motion';

export default function UseCasesSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-white py-32 border-t border-b border-white/5 relative z-10">

        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="bg-gray-50 border border-gray-200 p-16 rounded-3xl">
            <span className="font-mono text-xs text-indigo-400 tracking-widest uppercase mb-4 block">Component / use_cases</span>
            <h2 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6">
              Built for developersfor the agent-first era
            </h2>
            <p className="{cls['subtext']} text-xl max-w-2xl mx-auto mb-10">Google Antigravity is built for user trust, whether you're a professional developer working in a large enterprise codebase, a hobbyist vibe-coding in their spare time, or anyone in between.</p>
            <div className="flex gap-4 justify-center mt-8"><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">View case</button><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">View case</button></div>
          </div>
        </div>
      </section>
    </motion.div>
  );
}
