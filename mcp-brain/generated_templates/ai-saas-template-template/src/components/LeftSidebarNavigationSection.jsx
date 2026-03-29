import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function LeftSidebarNavigationSection() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', title: 'Dashboard' },
    { id: 'settings', title: 'Settings' },
    { id: 'security', title: 'Security' },
  ];

  return (
    <section className="py-32">
      <div className="container mx-auto p-8">
        <div className="bg-white border border-gray-200 rounded-[24px] p-8 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl">
          <h2 className="tracking-tight font-extrabold text-gray-500 mb-4">
            Left Sidebar Navigation
          </h2>
          <p className="text-gray-500 mb-8">
            Explore our intuitive navigation system, designed to simplify your workflow.
          </p>
          <div className="flex flex-wrap -mx-4 mb-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`px-4 py-2 rounded-full ${
                  activeTab === tab.id
                   ? 'bg-gray-900 text-white'
                    : 'bg-white border border-gray-200 text-gray-500'
                } transition-all duration-500 hover:bg-gray-900 hover:text-white`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.title}
              </button>
            ))}
          </div>
          <div className="bg-[#0a0a0a] border border-white/10 shadow-2xl rounded-3xl text-white p-4 mb-8">
            <h3 className="font-extrabold text-lg mb-2">
              {activeTab === 'dashboard'? 'Dashboard Overview' : ''}
              {activeTab === 'settings'? 'Settings Configuration' : ''}
              {activeTab === 'security'? 'Security Features' : ''}
            </h3>
            <p className="text-gray-300">
              {activeTab === 'dashboard'? (
                <span>
                  Get a bird's eye view of your project's progress, including key metrics and insights.
                </span>
              ) : (
                ''
              )}
              {activeTab === 'settings'? (
                <span>
                  Customize your project settings to fit your team's needs.
                </span>
              ) : (
                ''
              )}
              {activeTab === 'security'? (
                <span>
                  Protect your project with robust security features, including two-factor authentication and encryption.
                </span>
              ) : (
                ''
              )}
            </p>
          </div>
          <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"
            alt=" Navigation System"
            className="object-cover w-full h-48 rounded-3xl shadow-md mb-8"
          />
          <motion.button
            initial={{ scale: 1 }}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.5 }}
            className="bg-gray-900 text-white rounded-full px-4 py-2 shadow-md transition-transform"
          >
            Explore More
          </motion.button>
        </div>
      </div>
    </section>
  );
}