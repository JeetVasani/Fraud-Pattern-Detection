import Link from "next/link";


import Navigation from "./components/navigation-bar";
import Hero from "./components/hero";
import Contact from "./components/contact";

export default function Home() {
  return (
    
    <div className = "reveal-animate-main bg-[#0F0A1A]">
    <div className="flex flex-col min-h-screen px-8 bg-[#0F0A1A]">
      <main className="pt-20 space-y-20 grow">    
        <Navigation />
        <Hero />
        <Contact />
      </main>
    </div>
    </div>
  );
}
