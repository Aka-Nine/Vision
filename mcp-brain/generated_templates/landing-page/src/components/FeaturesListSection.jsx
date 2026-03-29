import React from 'react';
import { motion } from 'framer-motion';

export default function FeaturesListSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-gray-950 py-32 border-t border-b border-white/5 relative z-10">

        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">Features List</h2>

          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="bg-white/5 border border-white/10 backdrop-blur-lg h-[250px] p-8 rounded-2xl transition-all hover:-translate-y-2 hover:shadow-2xl flex flex-col justify-between">
                 <div className="w-12 h-12 rounded-full bg-white/10 mb-4"></div>
                 <h3 className="text-white text-xl font-bold">Feature {i}</h3>
              </div>
            ))}
          </div>
          <div className="flex gap-4 justify-center mt-8"><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">close</button></div>
        </div>
      </section>
    </motion.div>
  );
}
