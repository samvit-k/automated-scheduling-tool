import { ArrowRight, Brain, Upload, Palette } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import heroBackground from '@/assets/hero-background.jpg';

const benefits = [
  {
    icon: Brain,
    title: 'AI-Generated Schedules Tailored to You',
    description: 'Smart algorithms learn your preferences and create optimal schedules that fit your lifestyle.'
  },
  {
    icon: Upload,
    title: 'Upload Docs for Context-Aware Planning',
    description: 'Share your documents and let AI understand your commitments for more accurate scheduling.'
  },
  {
    icon: Palette,
    title: 'Beautiful Dark Interface for Focus',
    description: 'Elegantly designed dark theme that reduces eye strain and enhances productivity.'
  }
];

const scheduleEvents = [
  {
    time: '9:00 AM',
    duration: '2h',
    title: 'Morning Strategy Session',
    description: 'Review quarterly objectives and plan implementation',
    color: 'bg-blue-500/20 border-blue-500/30'
  },
  {
    time: '11:30 AM',
    duration: '1h 30m',
    title: 'Client Presentation Prep',
    description: 'Finalize slides and practice delivery',
    color: 'bg-amber-500/20 border-amber-500/30'
  },
  {
    time: '1:00 PM',
    duration: '1h',
    title: 'Lunch & Networking',
    description: 'Industry meetup at downtown café',
    color: 'bg-green-500/20 border-green-500/30'
  },
  {
    time: '3:00 PM',
    duration: '3h',
    title: 'Development Sprint',
    description: 'Focus time for feature implementation',
    color: 'bg-purple-500/20 border-purple-500/30'
  },
  {
    time: '6:00 PM',
    duration: '45m',
    title: 'Team Retrospective',
    description: 'Weekly team sync and feedback session',
    color: 'bg-pink-500/20 border-pink-500/30'
  }
];

export default function Landing() {
  return (
    <div className="min-h-screen pt-navbar">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        {/* Video Background */}
        <video
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
          poster={heroBackground}
        >
          <source src="/videos/hero-background.mp4" type="video/mp4" />
          <source src="/videos/hero-background.webm" type="video/webm" />
        </video>
        
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-black/40"></div>
        
        <div className="relative container-centered">
          <div className="text-center animate-fade-in">
            <h1 className="text-6xl lg:text-7xl font-bold text-white mb-8">
              Your AI-Powered Schedule,{' '}
              <span className="text-transparent bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text">
                Instantly
              </span>
            </h1>
            <p className="text-2xl lg:text-3xl text-gray-200 mb-10 max-w-4xl mx-auto font-serif">
              Turn your ideas into perfectly balanced plans in seconds. Let AI understand your commitments and create schedules that actually work for your life.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg" 
                asChild
                className="hover-lift transition-normal text-xl px-10 py-8"
              >
                <Link to="/signup">
                  Get Started for Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                asChild
                className="text-xl px-10 py-8 bg-white/10 border-white/20 text-white hover:bg-white/20 transition-normal"
              >
                <Link to="/workspace">View Demo</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-12 lg:py-16 bg-surface">
        <div className="container-centered">
          <div className="text-center mb-12">
            <h2 className="text-5xl lg:text-6xl font-bold mb-6">
              Why Choose ScheduleAI?
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto font-serif">
              Combining the power of artificial intelligence with intuitive design to revolutionize how you plan your time.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => (
              <Card 
                key={benefit.title}
                className="hover-lift transition-normal animate-slide-up border-card-border shadow-soft"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <CardHeader className="text-center">
                  <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <benefit.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center text-lg">
                    {benefit.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Schedule Preview Section */}
      <section className="py-12 lg:py-16">
        <div className="container-centered">
          <div className="text-center mb-12">
            <h2 className="text-5xl lg:text-6xl font-bold mb-6">
              See Your Perfect Schedule Come to Life
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto font-serif">
              Watch as AI transforms your requirements into beautifully organized, actionable schedules.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-card border border-card-border rounded-lg p-4 shadow-elevated animate-scale-in">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-border-subtle">
                <h3 className="text-2xl font-semibold flex items-center">
                  📅 Today's Schedule
                </h3>
                <span className="text-xs text-muted-foreground">Monday, July 21st, 2025</span>
              </div>
              
              <div className="space-y-3">
                {scheduleEvents.map((event, index) => (
                  <div 
                    key={event.title}
                    className={cn(
                      "p-4 rounded-lg border-2 transition-all duration-300 hover:shadow-soft",
                      event.color,
                      "animate-slide-up"
                    )}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-base font-semibold">{event.time}</span>
                          <span className="text-xs text-muted-foreground">{event.duration}</span>
                        </div>
                        <h4 className="text-lg font-semibold mb-1">{event.title}</h4>
                        <p className="text-sm text-muted-foreground">{event.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Button 
              size="lg" 
              asChild
              className="hover-lift transition-normal text-xl px-10 py-8"
            >
              <Link to="/signup">
                Start Planning Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}