import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm " +
          "ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none " +
          "focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export const Label: React.FC<React.LabelHTMLAttributes<HTMLLabelElement>> = ({ className, ...props }) => (
  <label className={cn("text-sm font-medium leading-none", className)} {...props} />
);

const badgeVariants: Record<string, string> = {
  default: "bg-primary text-primary-foreground",
  secondary: "bg-secondary text-secondary-foreground",
  success: "bg-green-500/15 text-green-600 dark:text-green-400",
  warning: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  destructive: "bg-destructive/15 text-destructive",
};

export const Badge: React.FC<React.HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof badgeVariants }> = ({
  className,
  variant = "default",
  ...props
}) => (
  <span
    className={cn(
      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
      badgeVariants[variant],
      className
    )}
    {...props}
  />
);

export const Progress: React.FC<{ value: number; className?: string }> = ({ value, className }) => (
  <div className={cn("h-2 w-full overflow-hidden rounded-full bg-secondary", className)}>
    <div
      className="h-full rounded-full bg-primary transition-all"
      style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
    />
  </div>
);
