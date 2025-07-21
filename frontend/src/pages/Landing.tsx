import { Link } from "react-router-dom";
import { Brain, FileText, Palette, ArrowRight, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import BenefitCard from "@/components/BenefitCard";
import Navigation from "@/components/Navigation";

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative pt-20 pb-32">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <div className="animate-fade-in">
            <h1 className="text-5xl lg:text-7xl font-bold text-foreground mb-8 font-display leading-tight">
              Your AI-Powered Schedule,{" "}
              <span className="text-primary">Instantly</span>
            </h1>
            
            <p className="text-xl lg:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto font-display font-normal leading-relaxed">
              Turn your ideas into perfectly balanced plans in seconds. 
              Upload documents, describe your goals, and watch AI create your ideal schedule.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link to="/workspace">
                <Button className="btn-hero group">
                  Get Started for Free
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-background">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16 animate-slide-up">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-6 font-display">
              Why Choose Schedulo?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Experience the future of planning with AI-powered intelligence and beautiful design.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="animate-scale-in" style={{ animationDelay: "0.1s" }}>
              <BenefitCard
                icon={<Brain className="h-6 w-6 text-white" />}
                title="AI-Generated Schedules"
                description="Smart algorithms analyze your preferences and constraints to create perfectly balanced schedules tailored to your unique needs."
                color="bg-warm-purple"
              />
            </div>
            
            <div className="animate-scale-in" style={{ animationDelay: "0.2s" }}>
              <BenefitCard
                icon={<FileText className="h-6 w-6 text-white" />}
                title="Context-Aware Planning"
                description="Upload documents, share your goals, and let our AI understand the full context to create truly intelligent schedules."
                color="bg-warm-orange"
              />
            </div>
            
            <div className="animate-scale-in" style={{ animationDelay: "0.3s" }}>
              <BenefitCard
                icon={<Palette className="h-6 w-6 text-white" />}
                title="Beautiful & Minimal Design"
                description="Switch between light and dark themes in a clean, distraction-free interface that keeps you focused on what matters."
                color="bg-warm-green"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Schedule Preview Section */}
      <section className="py-20 bg-secondary/30">
        <div className="max-w-5xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-6 font-display">
              See It In Action
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Watch how Schedulo transforms your requirements into a beautifully organized schedule.
            </p>
          </div>
          
          {/* Mock Schedule Preview */}
          <div className="card-elevated p-8 bg-card animate-slide-up max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-foreground font-display">
                Your Generated Schedule
              </h3>
              <Calendar className="h-5 w-5 text-primary" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-warm-purple/10 border border-warm-purple/20 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-warm-purple">9:00 AM</span>
                  <span className="text-xs text-muted-foreground">2h</span>
                </div>
                <h4 className="font-semibold text-foreground mb-1">Deep Work Session</h4>
                <p className="text-sm text-muted-foreground">Focus on project proposal</p>
              </div>
              
              <div className="bg-warm-orange/10 border border-warm-orange/20 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-warm-orange">1:00 PM</span>
                  <span className="text-xs text-muted-foreground">1h</span>
                </div>
                <h4 className="font-semibold text-foreground mb-1">Team Meeting</h4>
                <p className="text-sm text-muted-foreground">Weekly sync & planning</p>
              </div>
              
              <div className="bg-warm-green/10 border border-warm-green/20 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-warm-green">3:30 PM</span>
                  <span className="text-xs text-muted-foreground">30m</span>
                </div>
                <h4 className="font-semibold text-foreground mb-1">Break & Refresh</h4>
                <p className="text-sm text-muted-foreground">Recharge for afternoon tasks</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-background">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-6 font-display">
            Ready to Transform Your Planning?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users who have revolutionized their productivity with AI-powered scheduling.
          </p>
          
          <Link to="/workspace">
            <Button className="btn-hero group">
              Start Planning Now
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Landing;