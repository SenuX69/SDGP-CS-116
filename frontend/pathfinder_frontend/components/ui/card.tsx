"use client";

import React from "react";

type CardProps = React.HTMLAttributes<HTMLDivElement> & { children: React.ReactNode };

export function Card({ children, className = "", ...rest }: CardProps) {
  return (
    <div
      className={["rounded-lg border p-5 bg-white shadow-sm h-full", className]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "", ...rest }: CardProps) {
  return (
    <div className={["flex flex-row items-center gap-3", className].join(" ")} {...rest}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = "", ...rest }: CardProps) {
  return (
    <h3 className={["text-lg font-medium", className].join(" ")} {...rest}>
      {children}
    </h3>
  );
}

export function CardContent({ children, className = "", ...rest }: CardProps) {
  return (
    <div className={["text-slate-600 mt-2", className].join(" ")} {...rest}>
      {children}
    </div>
  );
}

export default Card;
