import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import LandingWorkspace from '../components/landing/LandingWorkspace';
import HowItWorks from '../components/landing/HowItWorks';
import Capabilities from '../components/landing/Capabilities';
import UseCases from '../components/landing/UseCases';
import CTA from '../components/landing/CTA';
import Footer from '../components/landing/Footer';

export default function Home({ navigateTo }) {
  return (
    <div>
      <Navbar navigateTo={navigateTo} />
      <Hero navigateTo={navigateTo} />
      <LandingWorkspace navigateTo={navigateTo} />
      <HowItWorks />
      <Capabilities />
      <UseCases />
      <CTA />
      <Footer />
    </div>
  );
}
