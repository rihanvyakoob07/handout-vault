import React from "react";
import { cn } from "./../../lib/utils";

export const Input = React.forwardRef(({ className, ...props }, ref) => (
  <input
    className={cn(
      "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-400 outline-none",
      className
    )}
    ref={ref}
    {...props}
  />
));
Input.displayName = "Input";
