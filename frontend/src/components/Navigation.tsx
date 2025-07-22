import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';

import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Home', href: '/' },
  { name: 'Workspace', href: '/workspace' },
  { name: 'Pricing', href: '/pricing' },
];

export function Navigation() {
  const location = useLocation();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border-subtle">
      <div className="container-centered">
        <div className="flex items-center justify-between h-navbar">
          {/* Logo */}
          <Link 
            to="/" 
            className="text-2xl font-serif font-semibold hover:text-primary transition-fast"
          >
            ScheduleAI
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "text-base font-medium transition-fast hover:text-primary",
                  location.pathname === item.href
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {location.pathname !== '/login' && location.pathname !== '/signup' && (
              <div className="flex items-center space-x-3">
                <Button 
                  variant="ghost" 
                  size="default" 
                  asChild
                  className="hover-glow transition-fast text-base"
                >
                  <Link to="/login">Log in</Link>
                </Button>
                <Button 
                  size="default" 
                  asChild
                  className="hover-glow transition-fast text-base"
                >
                  <Link to="/signup">Sign up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}