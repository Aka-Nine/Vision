import React, { useEffect } from 'react';
import Lenis from 'lenis';
import gsap from 'gsap';
import GlobalHeaderSection from '../components/GlobalHeaderSection';
import LeftSidebarNavigationSection from '../components/LeftSidebarNavigationSection';
import PinDetailCardContainerSection from '../components/PinDetailCardContainerSection';
import RelatedPinsGridSection from '../components/RelatedPinsGridSection';

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
    <main className="min-h-screen bg-gray-950">
        <GlobalHeaderSection />
        <LeftSidebarNavigationSection />
        <PinDetailCardContainerSection />
        <RelatedPinsGridSection />
    </main>
  );
}
