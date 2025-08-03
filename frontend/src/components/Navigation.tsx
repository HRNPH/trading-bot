import React from "react";
import { TrendingUp, Menu } from "lucide-react";

const Navigation: React.FC = () => {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-4">
            <TrendingUp className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">Trading Bot Platform</span>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <a
              href="/"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Dashboard
            </a>
          </div>

          <div className="md:hidden">
            <Menu className="h-6 w-6" />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
