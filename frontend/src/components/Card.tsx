import { PropsWithChildren } from "react";

interface CardProps extends PropsWithChildren {
  title?: string;
  id?: string;
  actions?: React.ReactNode;
}

export default function Card({ title, id, actions, children }: CardProps) {
  return (
    <section
      id={id}
      className="rounded-xl border border-neutral-800/60 bg-gradient-to-b from-neutral-900/60 to-neutral-950/60 shadow-sm shadow-black/30"
    >
      <div className="flex items-center justify-between px-5 py-4 border-b border-neutral-800/60">
        <h2 className="text-base font-semibold tracking-tight">{title}</h2>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      <div className="px-5 py-5">{children}</div>
    </section>
  );
}
