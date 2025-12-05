import React from "react";
import { cn } from "./../../lib/utils";

export const Button = ({ className, ...props }) => {
  return (
    <button
      className={cn(
        "px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition",
        className
      )}
      {...props}
    />
  );
};
