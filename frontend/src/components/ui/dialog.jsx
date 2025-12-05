import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "./../../lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;

export function DialogContent({ className, ...props }) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40" />
      <DialogPrimitive.Content
        className={cn(
          "fixed z-50 bg-white p-6 rounded-lg shadow-lg top-[50%] left-[50%] w-full max-w-md translate-x-[-50%] translate-y-[-50%]",
          className
        )}
        {...props}
      />
    </DialogPrimitive.Portal>
  );
}

export const DialogHeader = ({ children }) => (
  <div className="mb-4">{children}</div>
);

export const DialogTitle = ({ children }) => (
  <h3 className="text-lg font-semibold">{children}</h3>
);
