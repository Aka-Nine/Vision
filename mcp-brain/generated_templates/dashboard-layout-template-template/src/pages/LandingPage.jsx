import React from 'react';
import HeroDisplayPosterSection from '../components/HeroDisplayPosterSection';
import SidebarNavigationSection from '../components/SidebarNavigationSection';
import HeaderBarSection from '../components/HeaderBarSection';
import DataOverviewCardsSection from '../components/DataOverviewCardsSection';
import SalesAndMetricsVisualizationSection from '../components/SalesAndMetricsVisualizationSection';
import ListAndDetailsPanelsSection from '../components/ListAndDetailsPanelsSection';
import PromotionalActionCardsSection from '../components/PromotionalActionCardsSection';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-950">
        <HeroDisplayPosterSection />
        <SidebarNavigationSection />
        <HeaderBarSection />
        <DataOverviewCardsSection />
        <SalesAndMetricsVisualizationSection />
        <ListAndDetailsPanelsSection />
        <PromotionalActionCardsSection />
    </main>
  );
}
