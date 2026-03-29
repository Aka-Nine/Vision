import React from 'react';
import { motion } from 'framer-motion';

export default function BottomNavigationBarSection() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <section className="bg-gray-950 py-24">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            Bottom Navigation Bar
          </h2>
          <p className="text-gray-400 text-lg">
            Content for the Bottom Navigation Bar section.
          </p>
        </div>
      </section>
    </motion.div>
  );
}
