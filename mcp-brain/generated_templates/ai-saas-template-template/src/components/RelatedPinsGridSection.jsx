import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function RelatedPinsGridSection() {
  const [activeTab, setActiveTab] = useState('tab1');

  return (
    <motion.section
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="py-32 bg-slate-50"
    >
      <div className="container mx-auto px-4 md:px-6 xl:px-12 2xl:px-16">
        <div className="text-center mb-12">
          <motion.h2
            initial={{ y: 20 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true }}
            className="tracking-tight font-extrabold text-4xl text-gray-500"
          >
            Related Pins Grid
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-gray-500 text-lg"
          >
            Discover more from our community of creators
          </motion.p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
          >
            <img
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"
              alt="Image"
              className="w-full h-48 object-cover rounded-[24px] mb-4"
            />
            <h3 className="font-bold text-lg text-gray-500 mb-2">Tab 1</h3>
            <p className="text-gray-500 text-sm">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit
              amet nulla auctor, vestibulum magna sed, convallis ex.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
          >
            <img
              src="https://images.unsplash.com/photo-1542831371-29b0f74f9713?q=80&w=2070&auto=format&fit=crop"
              alt="Image"
              className="w-full h-48 object-cover rounded-[24px] mb-4"
            />
            <h3 className="font-bold text-lg text-gray-500 mb-2">Tab 2</h3>
            <p className="text-gray-500 text-sm">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit
              amet nulla auctor, vestibulum magna sed, convallis ex.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
          >
            <img
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"
              alt="Image"
              className="w-full h-48 object-cover rounded-[24px] mb-4"
            />
            <h3 className="font-bold text-lg text-gray-500 mb-2">Tab 3</h3>
            <p className="text-gray-500 text-sm">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit
              amet nulla auctor, vestibulum magna sed, convallis ex.
            </p>
          </motion.div>
        </div>
        <div className="flex justify-center mt-12">
          <button
            className={`${
              activeTab === 'tab1'
               ? 'bg-gray-900 text-white'
                : 'bg-gray-200 text-gray-500'
            } rounded-full px-4 py-2 transition-transform duration-200 hover:scale-105 shadow-md`}
            onClick={() => setActiveTab('tab1')}
          >
            Tab 1
          </button>
          <button
            className={`${
              activeTab === 'tab2'
               ? 'bg-gray-900 text-white'
                : 'bg-gray-200 text-gray-500'
            } rounded-full px-4 py-2 transition-transform duration-200 hover:scale-105 shadow-md mx-4`}
            onClick={() => setActiveTab('tab2')}
          >
            Tab 2
          </button>
          <button
            className={`${
              activeTab === 'tab3'
               ? 'bg-gray-900 text-white'
                : 'bg-gray-200 text-gray-500'
            } rounded-full px-4 py-2 transition-transform duration-200 hover:scale-105 shadow-md`}
            onClick={() => setActiveTab('tab3')}
          >
            Tab 3
          </button>
        </div>
      </div>
    </motion.section>
  );
}