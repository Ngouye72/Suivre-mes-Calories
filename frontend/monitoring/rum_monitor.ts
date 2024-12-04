import { BrowserTracing } from '@sentry/tracing';
import * as Sentry from '@sentry/react-native';
import { Metrics } from '@opentelemetry/api';
import { WebVitals } from 'web-vitals';
import { NavigationState } from '@react-navigation/native';

interface PerformanceMetrics {
    fcp: number;  // First Contentful Paint
    lcp: number;  // Largest Contentful Paint
    fid: number;  // First Input Delay
    cls: number;  // Cumulative Layout Shift
    ttfb: number; // Time to First Byte
    navigationTiming: NavigationTiming;
    resourceTiming: ResourceTiming[];
    errors: ErrorMetric[];
    interactions: UserInteraction[];
}

interface NavigationTiming {
    startTime: number;
    duration: number;
    type: string;
    redirectCount: number;
}

interface ResourceTiming {
    name: string;
    startTime: number;
    duration: number;
    initiatorType: string;
    size: number;
}

interface ErrorMetric {
    timestamp: number;
    type: string;
    message: string;
    component?: string;
}

interface UserInteraction {
    timestamp: number;
    type: string;
    target: string;
    duration?: number;
}

class RUMMonitor {
    private static instance: RUMMonitor;
    private metrics: Metrics;
    private performanceData: PerformanceMetrics;
    private sessionId: string;

    private constructor() {
        // Initialisation Sentry pour le tracking frontend
        Sentry.init({
            dsn: 'your-sentry-dsn',
            integrations: [new BrowserTracing()],
            tracesSampleRate: 1.0,
            environment: process.env.NODE_ENV
        });

        this.sessionId = this.generateSessionId();
        this.initializeMetrics();
        this.setupPerformanceObservers();
        this.setupErrorTracking();
        this.setupInteractionTracking();
    }

    public static getInstance(): RUMMonitor {
        if (!RUMMonitor.instance) {
            RUMMonitor.instance = new RUMMonitor();
        }
        return RUMMonitor.instance;
    }

    private generateSessionId(): string {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    private initializeMetrics(): void {
        this.performanceData = {
            fcp: 0,
            lcp: 0,
            fid: 0,
            cls: 0,
            ttfb: 0,
            navigationTiming: {
                startTime: 0,
                duration: 0,
                type: '',
                redirectCount: 0
            },
            resourceTiming: [],
            errors: [],
            interactions: []
        };

        // Initialisation Web Vitals
        WebVitals.getFCP(metric => {
            this.performanceData.fcp = metric.value;
            this.sendMetric('fcp', metric.value);
        });

        WebVitals.getLCP(metric => {
            this.performanceData.lcp = metric.value;
            this.sendMetric('lcp', metric.value);
        });

        WebVitals.getFID(metric => {
            this.performanceData.fid = metric.value;
            this.sendMetric('fid', metric.value);
        });

        WebVitals.getCLS(metric => {
            this.performanceData.cls = metric.value;
            this.sendMetric('cls', metric.value);
        });
    }

    private setupPerformanceObservers(): void {
        // Observer pour les performances de navigation
        const navigationObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'navigation') {
                    this.performanceData.navigationTiming = {
                        startTime: entry.startTime,
                        duration: entry.duration,
                        type: entry.type,
                        redirectCount: (entry as PerformanceNavigationTiming).redirectCount
                    };
                    this.sendMetric('navigation', entry.duration);
                }
            }
        });

        // Observer pour les performances des ressources
        const resourceObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                const resourceTiming = {
                    name: entry.name,
                    startTime: entry.startTime,
                    duration: entry.duration,
                    initiatorType: entry.initiatorType,
                    size: (entry as PerformanceResourceTiming).transferSize || 0
                };
                this.performanceData.resourceTiming.push(resourceTiming);
                this.sendMetric('resource', entry.duration, { 
                    resource: entry.name,
                    type: entry.initiatorType
                });
            }
        });

        navigationObserver.observe({ entryTypes: ['navigation'] });
        resourceObserver.observe({ entryTypes: ['resource'] });
    }

    private setupErrorTracking(): void {
        window.addEventListener('error', (event) => {
            const errorMetric: ErrorMetric = {
                timestamp: Date.now(),
                type: 'error',
                message: event.error?.message || 'Unknown error',
                component: this.getCurrentComponent()
            };
            this.performanceData.errors.push(errorMetric);
            this.sendMetric('error', 1, { 
                type: errorMetric.type,
                component: errorMetric.component
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            const errorMetric: ErrorMetric = {
                timestamp: Date.now(),
                type: 'promise_rejection',
                message: event.reason?.message || 'Unhandled Promise rejection',
                component: this.getCurrentComponent()
            };
            this.performanceData.errors.push(errorMetric);
            this.sendMetric('unhandled_rejection', 1, {
                component: errorMetric.component
            });
        });
    }

    private setupInteractionTracking(): void {
        const interactionObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                const interaction: UserInteraction = {
                    timestamp: Date.now(),
                    type: entry.name,
                    target: entry.target?.toString() || '',
                    duration: entry.duration
                };
                this.performanceData.interactions.push(interaction);
                this.sendMetric('interaction', entry.duration, {
                    type: entry.name,
                    target: entry.target?.toString() || ''
                });
            }
        });

        interactionObserver.observe({ entryTypes: ['measure'] });

        // Tracking des clics et interactions utilisateur
        document.addEventListener('click', (event) => {
            const interaction: UserInteraction = {
                timestamp: Date.now(),
                type: 'click',
                target: (event.target as HTMLElement).tagName,
            };
            this.performanceData.interactions.push(interaction);
            this.sendMetric('click', 1, {
                target: interaction.target
            });
        });
    }

    private getCurrentComponent(): string {
        // À implémenter selon votre système de routing
        return 'unknown';
    }

    public trackNavigation(state: NavigationState): void {
        const route = state.routes[state.index];
        this.sendMetric('navigation', Date.now(), {
            route: route.name,
            params: JSON.stringify(route.params)
        });
    }

    public trackUserAction(action: string, details: any = {}): void {
        const interaction: UserInteraction = {
            timestamp: Date.now(),
            type: action,
            target: details.target || '',
            duration: details.duration
        };
        this.performanceData.interactions.push(interaction);
        this.sendMetric('user_action', 1, {
            action,
            ...details
        });
    }

    public trackApiCall(endpoint: string, duration: number, status: number): void {
        this.sendMetric('api_call', duration, {
            endpoint,
            status: status.toString()
        });
    }

    private sendMetric(name: string, value: number, tags: Record<string, string> = {}): void {
        // Envoi à Prometheus/OpenTelemetry
        this.metrics.record(name, {
            value,
            tags: {
                ...tags,
                sessionId: this.sessionId,
                environment: process.env.NODE_ENV
            }
        });

        // Envoi à Sentry pour le tracking
        Sentry.addBreadcrumb({
            category: 'performance',
            message: `${name}: ${value}`,
            data: tags
        });
    }

    public getPerformanceReport(): PerformanceMetrics {
        return this.performanceData;
    }

    public analyzePerformance(): any {
        const report = {
            webVitals: {
                fcp: this.analyzeMetric(this.performanceData.fcp, 2500),
                lcp: this.analyzeMetric(this.performanceData.lcp, 4000),
                fid: this.analyzeMetric(this.performanceData.fid, 100),
                cls: this.analyzeMetric(this.performanceData.cls, 0.1),
            },
            resources: this.analyzeResources(),
            errors: this.analyzeErrors(),
            interactions: this.analyzeInteractions(),
            recommendations: this.generateRecommendations()
        };

        return report;
    }

    private analyzeMetric(value: number, threshold: number): string {
        if (value <= threshold * 0.75) return 'good';
        if (value <= threshold) return 'needs-improvement';
        return 'poor';
    }

    private analyzeResources(): any {
        const slowResources = this.performanceData.resourceTiming
            .filter(r => r.duration > 1000)
            .map(r => ({
                name: r.name,
                duration: r.duration,
                size: r.size
            }));

        return {
            slowResources,
            totalResources: this.performanceData.resourceTiming.length,
            averageLoadTime: this.calculateAverage(
                this.performanceData.resourceTiming.map(r => r.duration)
            )
        };
    }

    private analyzeErrors(): any {
        return {
            totalErrors: this.performanceData.errors.length,
            errorsByType: this.groupBy(
                this.performanceData.errors,
                'type'
            ),
            errorsByComponent: this.groupBy(
                this.performanceData.errors,
                'component'
            )
        };
    }

    private analyzeInteractions(): any {
        return {
            totalInteractions: this.performanceData.interactions.length,
            averageInteractionTime: this.calculateAverage(
                this.performanceData.interactions
                    .filter(i => i.duration)
                    .map(i => i.duration!)
            ),
            interactionsByType: this.groupBy(
                this.performanceData.interactions,
                'type'
            )
        };
    }

    private calculateAverage(numbers: number[]): number {
        return numbers.length ? 
            numbers.reduce((a, b) => a + b, 0) / numbers.length : 
            0;
    }

    private groupBy(array: any[], key: string): Record<string, number> {
        return array.reduce((result, item) => {
            const group = item[key];
            result[group] = (result[group] || 0) + 1;
            return result;
        }, {});
    }

    private generateRecommendations(): string[] {
        const recommendations: string[] = [];

        // Web Vitals
        if (this.performanceData.lcp > 4000) {
            recommendations.push(
                'Le LCP est élevé. Optimisez le chargement du contenu principal.'
            );
        }

        if (this.performanceData.fid > 100) {
            recommendations.push(
                'Le FID est élevé. Optimisez la réactivité aux interactions.'
            );
        }

        // Ressources
        const slowResources = this.performanceData.resourceTiming
            .filter(r => r.duration > 1000);
        if (slowResources.length > 0) {
            recommendations.push(
                `${slowResources.length} ressources sont lentes à charger. Considérez l'optimisation.`
            );
        }

        // Erreurs
        if (this.performanceData.errors.length > 0) {
            recommendations.push(
                `${this.performanceData.errors.length} erreurs détectées. Examinez les logs.`
            );
        }

        return recommendations;
    }
}

export const rumMonitor = RUMMonitor.getInstance();
