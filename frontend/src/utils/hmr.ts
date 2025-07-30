/**
 * HMR (Hot Module Replacement) Utilities
 * 
 * This file contains utilities to ensure proper HMR behavior for React hooks and components.
 * These patterns prevent common HMR issues where hooks are misidentified as components.
 */

/**
 * Creates an HMR-safe hook factory that maintains stable references across hot reloads.
 * 
 * @param hookFactory - A function that returns the actual hook
 * @param hookName - Optional name for debugging purposes
 * @returns A stable hook reference that works correctly with HMR
 */
export function createStableHook<T extends (...args: any[]) => any>(
  hookFactory: () => T,
  hookName?: string
): T {
  const hook = hookFactory()
  
  // Mark as a hook for better HMR tracking
  ;(hook as any)._isHook = true
  
  // Set display name for debugging
  if (hookName) {
    ;(hook as any).displayName = hookName
  }
  
  return hook
}

/**
 * Creates an HMR-safe context provider with stable references.
 * 
 * @param Provider - The context provider component
 * @param displayName - Display name for debugging
 * @returns A memoized provider that maintains stable references
 */
export function createStableProvider<T extends React.ComponentType<any>>(
  Provider: T,
  displayName: string
): T {
  const StableProvider = React.memo(Provider) as T
  StableProvider.displayName = displayName
  return StableProvider
}

/**
 * Ensures HMR accepts updates for the current module.
 * Call this at the end of files that export hooks or components.
 */
export function enableHMR(): void {
  if (import.meta.hot) {
    import.meta.hot.accept()
  }
}

/**
 * Type guard to check if a function is marked as a hook.
 */
export function isHook(fn: any): boolean {
  return typeof fn === 'function' && fn._isHook === true
}

/**
 * Decorator for marking functions as hooks to help with HMR detection.
 */
export function markAsHook<T extends Function>(hookFn: T): T {
  ;(hookFn as any)._isHook = true
  return hookFn
}

// Re-export React for convenience
import React from 'react'
export { React }