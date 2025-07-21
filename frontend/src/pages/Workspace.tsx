import { useState } from "react";
import { Send, Plus, Calendar, Clock, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import Navigation from "@/components/Navigation";

interface ScheduleEvent {
  id: string;
  title: string;
  time: string;
  duration: string;
  description: string;
  color: string;
}

const Workspace = () => {
  const [prompt, setPrompt] = useState("");
  const [events, setEvents] = useState<ScheduleEvent[]>([
    {
      id: "1",
      title: "Morning Strategy Session",
      time: "9:00 AM",
      duration: "2h",
      description: "Review quarterly objectives and plan implementation",
      color: "bg-warm-purple"
    },
    {
      id: "2",
      title: "Client Presentation Prep",
      time: "11:30 AM",
      duration: "1h 30m",
      description: "Finalize slides and practice delivery",
      color: "bg-warm-orange"
    },
    {
      id: "3",
      title: "Lunch & Networking",
      time: "1:00 PM",
      duration: "1h",
      description: "Industry meetup at downtown cafe",
      color: "bg-warm-green"
    },
    {
      id: "4",
      title: "Development Sprint",
      time: "3:00 PM",
      duration: "3h",
      description: "Focus time for feature implementation",
      color: "bg-primary"
    },
    {
      id: "5",
      title: "Team Retrospective",
      time: "6:00 PM",
      duration: "45m",
      description: "Weekly team sync and feedback session",
      color: "bg-warm-pink"
    }
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    // Here you would integrate with your AI service
    console.log("Generating schedule for:", prompt);
    setPrompt("");
  };

  const handleFileUpload = () => {
    // Handle file upload logic
    console.log("Upload file clicked");
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 pt-8 pb-20">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-foreground mb-3 font-display">
            Your AI Workspace
          </h1>
          <p className="text-lg text-muted-foreground">
            Describe your goals and watch AI create the perfect schedule for you.
          </p>
        </div>

        {/* Schedule Display */}
        <div className="mb-8 animate-slide-up">
          <div className="card-elevated p-6 bg-card">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Calendar className="h-6 w-6 text-primary" />
                <h2 className="text-2xl font-semibold text-foreground font-display">
                  Today's Schedule
                </h2>
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Monday, July 21st, 2025
              </div>
            </div>
            
            {/* Schedule Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {events.map((event, index) => (
                <div
                  key={event.id}
                  className={`${event.color}/10 border border-current/20 rounded-xl p-4 hover:scale-[1.02] transition-all duration-300 cursor-pointer animate-scale-in`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-sm font-medium ${event.color.replace('bg-', 'text-')}`}>
                      {event.time}
                    </span>
                    <span className="text-xs text-muted-foreground bg-background/50 px-2 py-1 rounded-md">
                      {event.duration}
                    </span>
                  </div>
                  <h3 className="font-semibold text-foreground mb-2 leading-tight">
                    {event.title}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {event.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Prompt Interface */}
        <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
          <div className="prompt-bar p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <Textarea
                    placeholder="Type your request here... (e.g., 'Schedule a productive Monday with 2 hours of deep work, team meetings, and time for lunch')"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="min-h-[100px] resize-none border-0 bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleFileUpload}
                    className="text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Upload Files
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    Add context documents
                  </span>
                </div>
                
                <Button
                  type="submit"
                  disabled={!prompt.trim()}
                  className="btn-hero px-6 py-2 text-sm"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Generate Schedule
                </Button>
              </div>
            </form>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 animate-fade-in" style={{ animationDelay: "0.4s" }}>
          <h3 className="text-lg font-semibold text-foreground mb-4 font-display">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="text-left p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-primary-soft transition-all duration-300">
              <FileText className="h-5 w-5 text-primary mb-2" />
              <div className="font-medium text-foreground mb-1">Import Calendar</div>
              <div className="text-sm text-muted-foreground">Sync with existing calendars</div>
            </button>
            
            <button className="text-left p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-primary-soft transition-all duration-300">
              <Calendar className="h-5 w-5 text-primary mb-2" />
              <div className="font-medium text-foreground mb-1">Template Library</div>
              <div className="text-sm text-muted-foreground">Choose from pre-built schedules</div>
            </button>
            
            <button className="text-left p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-primary-soft transition-all duration-300">
              <Clock className="h-5 w-5 text-primary mb-2" />
              <div className="font-medium text-foreground mb-1">Time Preferences</div>
              <div className="text-sm text-muted-foreground">Set your working hours</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Workspace;