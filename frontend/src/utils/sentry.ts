import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import { Integrations } from '@sentry/tracing';
import { RewriteFrames } from '@sentry/integrations';

interface SentryConfig {
  dsn: string;
  environment: string;
  release: string;
}

export const initSentry = (config: SentryConfig): void => {
  Sentry.init({
    dsn: config.dsn,
    environment: config.environment,
    release: config.release,
    
    // Performance monitoring
    integrations: [
      new BrowserTracing({
        tracingOrigins: ['localhost', 'nutrition-app.com'],
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
      new Integrations.BrowserTracing(),
      new RewriteFrames(),
    ],
    
    // Sample rates
    tracesSampleRate: 0.2,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    
    // Before send hook
    beforeSend(event) {
      // Don't send events in development
      if (process.env.NODE_ENV === 'development') {
        return null;
      }
      
      // Sanitize error messages
      if (event.exception) {
        sanitizeException(event.exception);
      }
      
      // Add custom context
      event.tags = {
        ...event.tags,
        'app.version': process.env.REACT_APP_VERSION,
        'app.buildNumber': process.env.REACT_APP_BUILD_NUMBER,
      };
      
      return event;
    },
    
    // Configure scope
    beforeScope(scope) {
      scope.setTag('app.name', 'nutrition-app');
      scope.setUser({
        id: localStorage.getItem('userId'),
        username: localStorage.getItem('username'),
      });
    },
  });
};

const sanitizeException = (exception: any): void => {
  if (exception.values) {
    exception.values.forEach((value: any) => {
      // Remove sensitive data from error messages
      if (value.value) {
        value.value = value.value.replace(/Bearer [a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+/g, 'Bearer [FILTERED]');
      }
      
      // Clean stack traces
      if (value.stacktrace && value.stacktrace.frames) {
        value.stacktrace.frames = value.stacktrace.frames.map((frame: any) => {
          // Remove local file paths
          if (frame.filename) {
            frame.filename = frame.filename.replace(/^.*[\\\/]/, '');
          }
          return frame;
        });
      }
    });
  }
};

export const captureError = (error: Error, context?: Record<string, any>): void => {
  Sentry.withScope((scope) => {
    if (context) {
      Object.entries(context).forEach(([key, value]) => {
        scope.setExtra(key, value);
      });
    }
    
    Sentry.captureException(error);
  });
};

export const setUserContext = (userId: string, userData: Record<string, any>): void => {
  Sentry.setUser({
    id: userId,
    ...userData,
  });
};

export const clearUserContext = (): void => {
  Sentry.setUser(null);
};

export const addBreadcrumb = (
  category: string,
  message: string,
  data?: Record<string, any>,
  level?: Sentry.Severity
): void => {
  Sentry.addBreadcrumb({
    category,
    message,
    data,
    level,
  });
};
