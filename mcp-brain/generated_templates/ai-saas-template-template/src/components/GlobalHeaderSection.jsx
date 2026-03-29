import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function GlobalHeaderSection() {
  const [activeTab, setActiveTab] = useState('features');

  return (
    <motion.section
      initial={{ y: 100, opacity: 0 }}
      whileInView={{ y: 0, opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 w-full z-50 backdrop-blur-md bg-slate-50"
    >
      <div className="container mx-auto p-8">
        <nav className="flex justify-between items-center py-4">
          <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"
            alt="Logo"
            className="w-24 h-24 rounded-full object-cover shadow-md"
          />
          <ul className="hidden md:flex items-center space-x-8">
            <li>
              <a
                href="#"
                className="text-gray-500 hover:text-gray-900 transition-colors duration-200"
              >
                Features
              </a>
            </li>
            <li>
              <a
                href="#"
                className="text-gray-500 hover:text-gray-900 transition-colors duration-200"
              >
                Pricing
              </a>
            </li>
            <li>
              <a
                href="#"
                className="text-gray-500 hover:text-gray-900 transition-colors duration-200"
              >
                About
              </a>
            </li>
          </ul>
          <button className="md:hidden rounded-full bg-gray-900 text-white py-2 px-4 shadow-md hover:bg-black hover:scale-105 transition-transform duration-200">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </nav>
      </div>
      <div className="container mx-auto p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl">
            <h2 className="text-3xl tracking-tight font-extrabold text-gray-900">
              Global Header
            </h2>
            <p className="text-gray-500">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit amet nulla auctor, vestibulum magna sed, convallis ex.
            </p>
            <ul className="list-none space-y-2 mt-4">
              <li>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                  />
                </svg>
                <span className="text-gray-500">Lorem ipsum dolor sit amet.</span>
              </li>
              <li>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                  />
                </svg>
                <span className="text-gray-500">Lorem ipsum dolor sit amet.</span>
              </li>
            </ul>
          </div>
          <div className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl">
            <h3 className="text-2xl tracking-tight font-extrabold text-gray-900">
              CTAs
            </h3>
            <button
              className="bg-[#0a0a0a] border border-white/10 shadow-2xl rounded-3xl text-white py-2 px-4 hover:bg-black hover:scale-105 transition-transform duration-200"
            >
              Sign Up
            </button>
            <button
              className="bg-[#0a0a0a] border border-white/10 shadow-2xl rounded-3xl text-white py-2 px-4 hover:bg-black hover:scale-105 transition-transform duration-200"
            >
              Learn More
            </button>
          </div>
        </div>
      </div>
    </motion.section>
  );
}