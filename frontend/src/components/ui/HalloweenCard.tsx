import * as React from "react"
import { cn } from "@/lib/utils"

interface HalloweenCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'neubrutalism' | 'lifted' | 'corners' | 'default'
}

export const HalloweenCard = React.forwardRef<HTMLDivElement, HalloweenCardProps>(
  ({ className, variant = 'neubrutalism', children, ...props }, ref) => {
    const variantStyles = {
      neubrutalism: "border-2 border-[#FF6B00] shadow-[6px_6px_0px_0px_rgba(255,107,0,0.8)] hover:shadow-[8px_8px_0px_0px_rgba(255,107,0,1)] transition-all",
      lifted: "border-2 border-[#8B00FF] shadow-[0px_8px_0px_0px_rgba(139,0,255,0.7)] hover:shadow-[0px_12px_0px_0px_rgba(139,0,255,0.9)] transition-all",
      corners: "border-2 border-[#00FF41] relative",
      default: "border border-[#FF6B00]/30"
    }

    return (
      <div
        ref={ref}
        className={cn(
          "relative bg-[#1a1a1a] rounded-xl overflow-hidden",
          variantStyles[variant],
          className
        )}
        {...props}
      >
        {variant === 'corners' && (
          <>
            <div className="absolute -top-0.5 -left-0.5 w-6 h-6 border-l-2 border-t-2 border-[#00FF41] rounded-tl-md" />
            <div className="absolute -top-0.5 -right-0.5 w-6 h-6 border-r-2 border-t-2 border-[#00FF41] rounded-tr-md" />
            <div className="absolute -bottom-0.5 -left-0.5 w-6 h-6 border-l-2 border-b-2 border-[#00FF41] rounded-bl-md" />
            <div className="absolute -bottom-0.5 -right-0.5 w-6 h-6 border-r-2 border-b-2 border-[#00FF41] rounded-br-md" />
          </>
        )}
        {children}
      </div>
    )
  }
)

HalloweenCard.displayName = "HalloweenCard"
