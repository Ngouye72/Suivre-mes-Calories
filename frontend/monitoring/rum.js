import * as opentelemetry from '@opentelemetry/api';
import { WebTracerProvider } from '@opentelemetry/web';
import { Resource } from '@opentelemetry/resources';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { BatchSpanProcessor } from '@opentelemetry/tracing';
import { CollectorTraceExporter } from '@opentelemetry/exporter-collector';
import { UserInteractionInstrumentation } from '@opentelemetry/instrumentation-user-interaction';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';

class RUMManager {
    constructor() {
        this.provider = null;
        this.tracer = null;
        this.metrics = {
            pageLoads: {},
            interactions: {},
            apiCalls: {},
            errors: {},
            performance: {}
        };
    }

    init() {
        // Configuration du provider OpenTelemetry
        this.provider = new WebTracerProvider({
            resource: new Resource({
                'service.name': 'nutrition-app-frontend',
                'deployment.environment': process.env.NODE_ENV
            })
        });

        // Configuration de l'exportateur
        const exporter = new CollectorTraceExporter({
            url: process.env.OTEL_COLLECTOR_URL || 'http://localhost:4318/v1/traces'
        });

        this.provider.addSpanProcessor(new BatchSpanProcessor(exporter));
        this.provider.register({
            contextManager: new ZoneContextManager()
        });

        // Initialisation des instrumentations
        new UserInteractionInstrumentation().init();
        new XMLHttpRequestInstrumentation().init();
        new FetchInstrumentation().init();
        new DocumentLoadInstrumentation().init();

        this.tracer = opentelemetry.trace.getTracer('nutrition-app-rum');

        // Mise en place des écouteurs d'événements
        this.setupPerformanceObserver();
        this.setupErrorTracking();
        this.setupNavigationTracking();
    }

    setupPerformanceObserver() {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                switch (entry.entryType) {
                    case 'largest-contentful-paint':
                        this.metrics.performance.lcp = entry.startTime;
                        break;
                    case 'first-input':
                        this.metrics.performance.fid = entry.processingStart - entry.startTime;
                        break;
                    case 'layout-shift':
                        if (!this.metrics.performance.cls) {
                            this.metrics.performance.cls = 0;
                        }
                        this.metrics.performance.cls += entry.value;
                        break;
                }
            }
        });

        observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    }

    setupErrorTracking() {
        window.addEventListener('error', (event) => {
            const span = this.tracer.startSpan('error');
            span.setAttribute('error.type', event.error?.name || 'Unknown');
            span.setAttribute('error.message', event.error?.message || 'Unknown error');
            span.setAttribute('error.stack', event.error?.stack || '');
            span.end();

            this.metrics.errors[event.error?.name || 'Unknown'] = 
                (this.metrics.errors[event.error?.name || 'Unknown'] || 0) + 1;
        });

        window.addEventListener('unhandledrejection', (event) => {
            const span = this.tracer.startSpan('unhandled_promise_rejection');
            span.setAttribute('error.type', 'UnhandledPromiseRejection');
            span.setAttribute('error.message', event.reason?.message || 'Unknown rejection');
            span.end();

            this.metrics.errors.UnhandledPromiseRejection = 
                (this.metrics.errors.UnhandledPromiseRejection || 0) + 1;
        });
    }

    setupNavigationTracking() {
        const navigationObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'navigation') {
                    const metrics = {
                        dnsTime: entry.domainLookupEnd - entry.domainLookupStart,
                        connectTime: entry.connectEnd - entry.connectStart,
                        ttfb: entry.responseStart - entry.requestStart,
                        domLoad: entry.domContentLoadedEventEnd - entry.navigationStart,
                        windowLoad: entry.loadEventEnd - entry.navigationStart
                    };

                    const span = this.tracer.startSpan('page_load');
                    Object.entries(metrics).forEach(([key, value]) => {
                        span.setAttribute(`navigation.${key}`, value);
                    });
                    span.end();

                    this.metrics.pageLoads[window.location.pathname] = metrics;
                }
            }
        });

        navigationObserver.observe({ entryTypes: ['navigation'] });
    }

    trackUserInteraction(action, details = {}) {
        const span = this.tracer.startSpan('user_interaction');
        span.setAttribute('interaction.type', action);
        Object.entries(details).forEach(([key, value]) => {
            span.setAttribute(`interaction.${key}`, value);
        });
        span.end();

        this.metrics.interactions[action] = (this.metrics.interactions[action] || 0) + 1;
    }

    trackApiCall(endpoint, duration, status) {
        if (!this.metrics.apiCalls[endpoint]) {
            this.metrics.apiCalls[endpoint] = {
                count: 0,
                totalDuration: 0,
                errors: 0
            };
        }

        this.metrics.apiCalls[endpoint].count++;
        this.metrics.apiCalls[endpoint].totalDuration += duration;

        if (status >= 400) {
            this.metrics.apiCalls[endpoint].errors++;
        }
    }

    getMetrics() {
        return {
            ...this.metrics,
            timestamp: Date.now()
        };
    }
}

export const rumManager = new RUMManager();

// Exemple d'utilisation
rumManager.init();

// Pour tracker une interaction utilisateur
export function trackUserAction(action, details) {
    rumManager.trackUserInteraction(action, details);
}

// Pour tracker un appel API
export function trackApiRequest(endpoint, duration, status) {
    rumManager.trackApiCall(endpoint, duration, status);
}
