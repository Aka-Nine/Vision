import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function PinDetailCardContainerSection() {
  const [tab, setTab] = useState('tab1');

  return (
    <section className="py-32 bg-slate-50">
      <div className="container mx-auto p-8">
        <h2 className="text-5xl tracking-tight font-extrabold text-gray-900">
          Pin Detail Card Container
        </h2>
        <p className="text-gray-500 text-lg">
          Get instant access to a vast library of high-quality pin images, 
          detailed descriptions, and seamless sharing options.
        </p>
        <div className="flex justify-center mt-8">
          <button
            className={`bg-gray-900 text-white rounded-full px-6 py-3 shadow-md transition-transform ${
              tab === 'tab1'? 'scale-105' : ''
            }`}
            onClick={() => setTab('tab1')}
          >
            Tab 1
          </button>
          <button
            className={`bg-gray-900 text-white rounded-full px-6 py-3 shadow-md transition-transform ${
              tab === 'tab2'? 'scale-105' : ''
            }`}
            onClick={() => setTab('tab2')}
          >
            Tab 2
          </button>
        </div>
        <div className="mt-8">
          {tab === 'tab1'? (
            <Tab1Content />
          ) : (
            <Tab2Content />
          )}
        </div>
      </div>
    </section>
  );
}

function Tab1Content() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
    >
      <h3 className="text-3xl tracking-tight font-extrabold text-gray-900">
        Detailed Descriptions
      </h3>
      <p className="text-gray-500 text-lg">
        Get instant access to a vast library of high-quality pin images, 
        detailed descriptions, and seamless sharing options.
      </p>
      <ul className="mt-4 list-disc list-inside text-gray-500 text-lg">
        <li> Detailed descriptions for each pin </li>
        <li> High-quality images for a professional look </li>
        <li> Seamless sharing options for social media </li>
      </ul>
    </motion.div>
  );
}

function Tab2Content() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
    >
      <h3 className="text-3xl tracking-tight font-extrabold text-gray-900">
        Advanced Filtering
      </h3>
      <p className="text-gray-500 text-lg">
        Get instant access to a vast library of high-quality pin images, 
        detailed descriptions, and seamless sharing options.
      </p>
      <ul className="mt-4 list-disc list-inside text-gray-500 text-lg">
        <li> Advanced filtering options for a tailored experience </li>
        <li> Categories and tags for easy discovery </li>
        <li> Sorting options for a personalized feed </li>
      </ul>
    </motion.div>
  );
}