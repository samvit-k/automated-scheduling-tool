import { useState } from 'react';
import { Plus, Send, Upload, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

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

export default function Workspace() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    // Simulate AI processing
    setTimeout(() => {
      setIsGenerating(false);
      setPrompt('');
    }, 2000);
  };

  const handleFileUpload = () => {
    // Handle file upload logic
    console.log('File upload triggered');
  };

  return (
    <div className="min-h-screen pt-navbar bg-background">
      <div className="container-centered py-8">
        {/* Schedule Display */}
        <div className="mb-8">
          <Card className="shadow-elevated border-card-border animate-fade-in">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-subtle">
                <h1 className="text-4xl font-semibold flex items-center">
                  📅 Today's Schedule
                </h1>
                <div className="flex items-center text-muted-foreground">
                  <Clock className="h-4 w-4 mr-2" />
                  <span className="text-sm">Monday, July 21st, 2025</span>
                </div>
              </div>
              
              <div className="space-y-4">
                {scheduleEvents.map((event, index) => (
                  <div 
                    key={event.title}
                    className={cn(
                      "p-6 rounded-lg border-2 transition-all duration-300 hover:shadow-soft animate-slide-up",
                      event.color
                    )}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-4 mb-2">
                          <span className="text-lg font-semibold">{event.time}</span>
                          <span className="text-sm text-muted-foreground bg-background/50 px-2 py-1 rounded-full">
                            {event.duration}
                          </span>
                        </div>
                        <h3 className="text-2xl font-semibold mb-2">{event.title}</h3>
                        <p className="text-muted-foreground">{event.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Prompt Interface */}
        <Card className="shadow-floating border-card-border animate-slide-up">
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleFileUpload}
                  className="flex items-center gap-2 hover-glow transition-fast"
                >
                  <Plus className="h-4 w-4" />
                  <Upload className="h-4 w-4" />
                </Button>
                
                <div className="flex-1 relative">
                  <Input
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Type your request here... (e.g., 'Schedule a 2-hour design review tomorrow morning')"
                    className="h-12 pr-12 input-focus text-base"
                    disabled={isGenerating}
                  />
                  <Button
                    type="submit"
                    size="sm"
                    disabled={!prompt.trim() || isGenerating}
                    className="absolute right-2 top-2 h-8 w-8 p-0 hover-glow transition-fast"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {isGenerating && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <span className="ml-2">AI is generating your schedule...</span>
                </div>
              )}
            </form>
            
            <div className="mt-4 text-xs text-muted-foreground text-center">
              💡 Try: "Add a 30-minute break after lunch" or "Move the client meeting to 2 PM"
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}