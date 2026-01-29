import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useSidebarStore } from '@/store/useSidebarStore';
import { cn } from '@/lib/utils';

export function DashboardLayout() {
  const { isCollapsed } = useSidebarStore();

  return (
    <div className="min-h-screen bg-muted/10 flex w-full overflow-x-hidden">
      {/* Sidebar is fixed, so it doesn't push the flex layout, we use margins to compensate */}
      <Sidebar />

      <main className={cn(
        "flex-1 flex flex-col min-h-screen transition-all duration-300 ease-in-out",
        isCollapsed ? "md:pl-20" : "md:pl-64"
      )}>
        <div className="flex-1 flex flex-col w-full min-w-0">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
