import React, { useEffect } from 'react';
import Lenis from 'lenis';
import gsap from 'gsap';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import VideoSection from '../components/VideoSection';
import AboutSection from '../components/AboutSection';
import UseCasesSection from '../components/UseCasesSection';
import Footer from '../components/Footer';

export default function LandingPage() {
  useEffect(() => {
    // Initialize high-end smooth scrolling and GSAP context
    const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);

    // Expose gsap globally for nested components if needed
    window.gsap = gsap;

    return () => lenis.destroy();
  }, []);

  return (
    <main className="min-h-screen bg-white">
        <Navbar />
        <HeroSection />
        <FeaturesSection />
        <VideoSection />
        <AboutSection />
        <UseCasesSection />
        <Footer />
    </main>
  );
}
