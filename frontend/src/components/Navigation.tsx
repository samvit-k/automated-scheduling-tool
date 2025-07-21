import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navigation = () => {
  const [darkMode, setDarkMode] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const isDark = localStorage.getItem("darkMode") === "true";
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem("darkMode", newDarkMode.toString());
    
    if (newDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <span className="font-display text-2xl font-semibold text-foreground">
              Schedulo
            </span>
          </Link>

          {/* Center Navigation - Only show on non-auth pages */}
          {location.pathname !== "/login" && (
            <div className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className={`btn-ghost ${
                  isActive("/") ? "text-primary bg-primary-soft" : ""
                }`}
              >
                Home
              </Link>
              <Link
                to="/workspace"
                className={`btn-ghost ${
                  isActive("/workspace") ? "text-primary bg-primary-soft" : ""
                }`}
              >
                Workspace
              </Link>
              <Link
                to="#"
                className="btn-ghost"
              >
                Pricing
              </Link>
            </div>
          )}

          {/* Right side controls */}
          <div className="flex items-center space-x-4">
            {/* Dark mode toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleDarkMode}
              className="h-9 w-9 rounded-lg"
            >
              {darkMode ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            {/* Auth buttons */}
            {location.pathname !== "/login" && (
              <Link to="/login">
                <Button variant="outline" className="rounded-lg">
                  Log in
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;