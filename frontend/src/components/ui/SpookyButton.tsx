"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface SpookyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
}

export const SpookyButton = React.forwardRef<HTMLButtonElement, SpookyButtonProps>(
  ({ className, variant = 'primary', children, ...props }, ref) => {
    const [isHovered, setIsHovered] = React.useState(false)

    const variantStyles = {
      primary: "bg-[#FF6B00] text-white border-2 border-[#FF6B00] hover:bg-[#ff8533] hover:shadow-[0_0_20px_rgba(255,107,0,0.8)]",
      secondary: "bg-[#8B00FF] text-white border-2 border-[#8B00FF] hover:bg-[#a333ff] hover:shadow-[0_0_20px_rgba(139,0,255,0.8)]",
      ghost: "bg-transparent text-[#00FF41] border-2 border-[#00FF41] hover:bg-[#00FF41]/10 hover:shadow-[0_0_20px_rgba(0,255,65,0.6)]"
    }

    return (
      <button
        ref={ref}
        className={cn(
          "relative px-6 py-3 font-bold uppercase tracking-wider rounded-lg transition-all duration-300 transform hover:scale-105",
          "shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)]",
          variantStyles[variant],
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        {...props}
      >
        {/* Glitch layers */}
        {isHovered && (
          <>
            <div className="absolute inset-0 bg-[#00FFFF] opacity-20 rounded-lg animate-pulse" style={{ clipPath: 'polygon(0 20%, 100% 20%, 100% 50%, 0 50%)' }} />
            <div className="absolute inset-0 bg-[#FF00FF] opacity-20 rounded-lg animate-pulse" style={{ clipPath: 'polygon(0 50%, 100% 50%, 100% 80%, 0 80%)', animationDelay: '0.1s' }} />
          </>
        )}
        <span className="relative z-10">{children}</span>
      </button>
    )
  }
)

SpookyButton.displayName = "SpookyButton"
