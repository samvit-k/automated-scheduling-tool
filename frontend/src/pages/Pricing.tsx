import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started with AI scheduling',
    features: [
      '5 AI-generated schedules per month',
      'Basic calendar integration',
      'Light and dark themes',
      'Email support'
    ],
    cta: 'Get Started',
    href: '/signup',
    popular: false
  },
  {
    name: 'Pro',
    price: '$12',
    period: 'per month',
    description: 'For professionals who need advanced scheduling',
    features: [
      'Unlimited AI-generated schedules',
      'Document upload and analysis',
      'Advanced calendar integrations',
      'Priority support',
      'Custom scheduling templates',
      'Team collaboration features'
    ],
    cta: 'Start Pro Trial',
    href: '/signup?plan=pro',
    popular: true
  },
  {
    name: 'Enterprise',
    price: '$20',
    period: 'per month',
    description: 'For teams and organizations at scale',
    features: [
      'Everything in Pro',
      'Unlimited team members',
      'SSO integration',
      'Custom AI training',
      'Dedicated support',
      'On-premise deployment'
    ],
    cta: 'Contact Sales',
    href: '/contact',
    popular: false
  }
];

export default function Pricing() {
  return (
    <div className="min-h-screen pt-navbar">
      <section className="py-16 lg:py-24">
        <div className="container-centered">
          <div className="text-center mb-16 animate-fade-in">
            <h1 className="text-6xl lg:text-7xl font-bold mb-8">
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-serif">
              Choose the plan that fits your needs. Upgrade or downgrade at any time.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, index) => (
              <Card 
                key={plan.name}
                className={cn(
                  "relative hover-lift transition-normal animate-slide-up",
                  plan.popular 
                    ? "border-primary shadow-floating ring-2 ring-primary/20" 
                    : "border-card-border shadow-soft"
                )}
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.period && (
                      <span className="text-muted-foreground ml-2">/{plan.period}</span>
                    )}
                  </div>
                  <CardDescription className="mt-2 text-base">
                    {plan.description}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Button 
                    asChild
                    variant={plan.popular ? "default" : "outline"}
                    className="w-full hover-glow transition-normal"
                  >
                    <Link to={plan.href}>{plan.cta}</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-16 text-center animate-fade-in">
            <p className="text-muted-foreground mb-4">
              Have questions about our plans?
            </p>
            <Button variant="outline" asChild className="hover-glow transition-normal">
              <Link to="/contact">Contact our team</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}