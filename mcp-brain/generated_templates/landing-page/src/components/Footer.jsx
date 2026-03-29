import React from 'react';

export default function Footer() {
  return (
    <footer className="{cls['section']} py-20 border-t border-white/10 relative z-10">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-12">
        <div>
          <h4 className="font-bold {cls['heading']} mb-6 text-lg">Product</h4>
          <ul className="space-y-4 {cls['subtext']}">
            <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold {cls['heading']} mb-6 text-lg">Company</h4>
          <ul className="space-y-4 {cls['subtext']}">
            <li><a href="#" className="hover:text-white transition-colors">About</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold {cls['heading']} mb-6 text-lg">Resources</h4>
          <ul className="space-y-4 {cls['subtext']}">
            <li><a href="#" className="hover:text-white transition-colors">Docs</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold {cls['heading']} mb-6 text-lg">Legal</h4>
          <ul className="space-y-4 {cls['subtext']}">
            <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-6 mt-16 pt-8 border-t border-white/5 text-center {cls['subtext']}">
        <p>&copy; 2026 Crafted dynamically by MCP Brain AI. Extracted from Market Intelligence.</p>
      </div>
    </footer>
  );
}
