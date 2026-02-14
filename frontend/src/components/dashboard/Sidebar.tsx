import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/useAuthStore';
import {
  Settings,
  LogOut,
  FlaskConical,
  Menu,
  X,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  Moon,
  Home
} from 'lucide-react';
import { Logo } from '@/components/logo';
import { useThemeStore } from '@/store/useThemeStore';
import { useSidebarStore } from '@/store/useSidebarStore';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const { pathname } = useLocation();
  const { logout, authUser } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const { isCollapsed, toggleCollapse } = useSidebarStore();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    {
      name: 'Drug Discovery',
      href: '/dashboard',
      icon: FlaskConical,
    },
    {
      name: 'Settings',
      href: '/dashboard/settings',
      icon: Settings,
    },
  ];

  const toggleMobileSidebar = () => setIsOpen(!isOpen);
  const toggleDesktopSidebar = () => toggleCollapse();

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button variant="outline" size="icon" onClick={toggleMobileSidebar}>
          {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Sidebar Container */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-40 bg-background border-r transform transition-all duration-300 ease-in-out",
        // Mobile behavior
        isOpen ? "translate-x-0 w-64" : "-translate-x-full md:translate-x-0",
        // Desktop collapse behavior
        isCollapsed ? "md:w-20" : "md:w-64",
        className
      )}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className={cn(
            "h-16 flex items-center border-b transition-all duration-300",
            isCollapsed ? "justify-center px-2 gap-2" : "justify-between px-4"
          )}>
            {!isCollapsed ? (
              <Link to="/" className="flex items-center gap-3 overflow-hidden group">
                <Logo className="h-8 w-auto flex-shrink-0 transition-transform group-hover:scale-105" />
                <span className="font-semibold text-base tracking-tight whitespace-nowrap text-foreground/90">Drug Discovery AI</span>
              </Link>
            ) : (
              <Logo className="h-8 w-auto" />
            )}

            <Button
              variant="ghost"
              size="icon"
              className="hidden md:flex flex-shrink-0 h-8 w-8 text-muted-foreground hover:text-foreground"
              onClick={toggleDesktopSidebar}
              title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
            >
              {isCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            </Button>
          </div>

          {/* Navigation */}
          <div className="flex-1 py-6 px-3 space-y-1 overflow-y-auto overflow-x-hidden">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setIsOpen(false)}
                title={isCollapsed ? item.name : undefined}
              >
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className={cn(
                    "w-full mb-1 transition-all duration-200",
                    isCollapsed ? "justify-center px-0" : "justify-start gap-3"
                  )}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {!isCollapsed && <span>{item.name}</span>}
                </Button>
              </Link>
            ))}
          </div>

          {/* Footer Actions */}
          <div className="p-4 border-t bg-muted/20 space-y-2">
            <Link to="/" onClick={() => setIsOpen(false)}>
              <Button
                variant="ghost"
                size={isCollapsed ? "icon" : "default"}
                className={cn("w-full mb-1", isCollapsed ? "justify-center" : "justify-start gap-3")}
              >
                <Home className="h-4 w-4" />
                {!isCollapsed && <span>Home</span>}
              </Button>
            </Link>

            <Button
              variant="ghost"
              size={isCollapsed ? "icon" : "default"}
              className={cn("w-full", isCollapsed ? "justify-center" : "justify-start gap-3")}
              onClick={toggleTheme}
            >
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              {!isCollapsed && <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>}
            </Button>

            <div className={cn(
              "flex items-center rounded-lg bg-background p-2 border",
              isCollapsed ? "justify-center" : "gap-3"
            )}>
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden flex-shrink-0">
                {authUser?.profilePic ? (
                  <img src={authUser.profilePic} alt="Profile" className="h-full w-full object-cover" />
                ) : (
                  <User className="h-4 w-4 text-primary" />
                )}
              </div>
              {!isCollapsed && (
                <div className="flex-1 min-w-0 overflow-hidden">
                  <p className="text-sm font-medium truncate">{authUser?.fullName}</p>
                </div>
              )}
            </div>

            <Button
              variant="outline"
              size={isCollapsed ? "icon" : "default"}
              className={cn(
                "w-full text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20",
                isCollapsed ? "justify-center" : "justify-start gap-2"
              )}
              onClick={() => logout()}
            >
              <LogOut className="h-4 w-4" />
              {!isCollapsed && <span>Logout</span>}
            </Button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
