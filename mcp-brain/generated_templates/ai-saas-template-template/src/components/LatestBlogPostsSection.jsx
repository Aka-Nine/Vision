import React from 'react';
        import { motion } from 'framer-motion';

        export default function LatestBlogPostsSection() {
          return (
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
              <section className="{cls['section']} py-32 border-t border-b border-white/5 relative z-10">

                <div className="max-w-4xl mx-auto px-6 text-center">
                  <div className="{cls['card']} p-16 rounded-3xl">
                    <span className="font-mono text-xs text-indigo-400 tracking-widest uppercase mb-4 block">Component / latest_blog_posts</span>
                    <h2 className="text-4xl md:text-6xl font-extrabold {cls['heading']} mb-6">
                      {title}
                    </h2>
                    <p className="{cls['subtext']} text-xl max-w-2xl mx-auto mb-10">Available at no charge</p>
                    <div className="flex gap-4 justify-center mt-8"><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">Download</button><button className="{cls['btn_primary']} px-8 py-3 rounded-xl font-semibold">Notify me</button></div>
                  </div>
                </div>
              </section>
            </motion.div>
          );
        }
