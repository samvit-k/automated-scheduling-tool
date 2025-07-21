import React from "react";

interface BenefitCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

const BenefitCard = ({ icon, title, description, color }: BenefitCardProps) => {
  return (
    <div className="card-benefit group">
      <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${color} mb-6`}>
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-foreground mb-3 font-display">
        {title}
      </h3>
      <p className="text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
};

export default BenefitCard;