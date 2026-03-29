import React from 'react';
import { motion } from 'framer-motion';

const testimonials = [
  { name: 'Sarah Chen', role: 'CTO at TechFlow', text: 'This platform cut our design-to-code time by 80%. Absolutely game-changing.' },
  { name: 'Marcus Rivera', role: 'Lead Designer', text: 'The AI-generated templates are surprisingly polished — our clients love them.' },
];

export default function TestimonialsSection() {
  return (
    <section className="{cls['section']} py-32 relative z-10 border-t border-white/5">
      <div className="max-w-5xl mx-auto px-6">
        <h2 className="text-4xl md:text-6xl font-bold {cls['heading']} text-center mb-20">
          Experience liftoff with the next-generation IDE
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {testimonials.map((t, i) => (
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} key={i}>
              <div className="{cls['card']} p-10 rounded-3xl">
                <p className="{cls['subtext']} text-xl italic mb-8">"{t.text}"</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-white/20"></div>
                  <div>
                    <p className="font-semibold {cls['heading']} text-lg">{t.name}</p>
                    <p className="{cls['subtext']}">{t.role}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
