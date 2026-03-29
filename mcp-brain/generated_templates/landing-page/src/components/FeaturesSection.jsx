import React from 'react';
import { motion } from 'framer-motion';

const features = [
  { title: 'Advanced Integration', description: 'Deep architecture combining native frameworks.', icon: '⚡' },
  { title: 'Performant Rendering', description: 'Zero layout shift using hybrid methodologies.', icon: '🎯' },
  { title: 'Data Abstraction', description: 'Robust state management spanning complex layers.', icon: '🔒' },
];

export default function FeaturesSection() {
  return (
    <section className="{cls['section']} py-24 relative z-10 border-t border-white/5">
      <div className="max-w-6xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-6xl font-bold {cls['heading']} mb-16">
          TurboQuant: Redefining AI efficiency with extreme compression
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} key={i}>
              <div className="{cls['card']} p-10 rounded-3xl transition-all hover:scale-[1.02] hover:shadow-2xl">
                <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-3xl mb-6 mx-auto">{f.icon}</div>
                <h3 className="text-2xl font-semibold {cls['heading']} mb-4">{f.title}</h3>
                <p className="{cls['subtext']} text-lg leading-relaxed">{f.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
