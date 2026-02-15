"use client"

import * as React from "react"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

export interface CheckboxProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  onCheckedChange?: (checked: boolean) => void
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => {
    return (
      <label className={cn("relative flex items-center cursor-pointer", className)}>
        <input
          type="checkbox"
          ref={ref}
          checked={checked}
          onChange={(e) => onCheckedChange?.(e.target.checked)}
          className="sr-only peer"
          {...props}
        />
        <div className={cn(
          "w-4 h-4 border rounded transition-all",
          "border-gray-600 peer-checked:bg-blue-600 peer-checked:border-blue-600",
          "peer-focus:ring-2 peer-focus:ring-blue-500/20",
          "flex items-center justify-center"
        )}>
          {checked && <Check className="w-3 h-3 text-white" />}
        </div>
      </label>
    )
  }
)
Checkbox.displayName = "Checkbox"

export { Checkbox }