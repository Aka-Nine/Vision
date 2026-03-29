import React, { useEffect } from 'react';
import Lenis from 'lenis';
import gsap from 'gsap';
import HeroSection from '../components/HeroSection';
import ProductVideoSection from '../components/ProductVideoSection';
import AgentFirstFeatureSectionSection from '../components/AgentFirstFeatureSectionSection';
import FeatureExplorerSection from '../components/FeatureExplorerSection';
import UseCasesCarouselSection from '../components/UseCasesCarouselSection';
import SolutionsOfferingsPricingSection from '../components/SolutionsOfferingsPricingSection';
import LatestBlogsCarouselSection from '../components/LatestBlogsCarouselSection';
import DownloadCallToActionSection from '../components/DownloadCallToActionSection';
import GlobalFooterSection from '../components/GlobalFooterSection';

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
        <HeroSection />
        <ProductVideoSection />
        <AgentFirstFeatureSectionSection />
        <FeatureExplorerSection />
        <UseCasesCarouselSection />
        <SolutionsOfferingsPricingSection />
        <LatestBlogsCarouselSection />
        <DownloadCallToActionSection />
        <GlobalFooterSection />
    </main>
  );
}
