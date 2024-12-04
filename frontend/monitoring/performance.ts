import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { UserInteractionInstrumentation } from '@opentelemetry/instrumentation-user-interaction';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { WebVitalsInstrumentation } from '@opentelemetry/instrumentation-web-vitals';

export class PerformanceMonitor {
    private static instance: PerformanceMonitor;
    private tracerProvider: WebTracerProvider;

    private constructor() {
        this.initializeTracing();
    }

    public static getInstance(): PerformanceMonitor {
        if (!PerformanceMonitor.instance) {
            PerformanceMonitor.instance = new PerformanceMonitor();
        }
        return PerformanceMonitor.instance;
    }

    private initializeTracing() {
        const resource = new Resource({
            [SemanticResourceAttributes.SERVICE_NAME]: 'nutrition-frontend',
            [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
            environment: process.env.NODE_ENV || 'production'
        });

        this.tracerProvider = new WebTracerProvider({
            resource: resource
        });

        const collector = new OTLPTraceExporter({
            url: '/api/telemetry/traces'
        });

        this.tracerProvider.addSpanProcessor(
            new BatchSpanProcessor(collector, {
                maxQueueSize: 100,
                scheduledDelayMillis: 500
            })
        );

        this.tracerProvider.register({
            contextManager: new ZoneContextManager()
        });

        registerInstrumentations({
            instrumentations: [
                new UserInteractionInstrumentation({
                    eventNames: ['click', 'submit']
                }),
                new XMLHttpRequestInstrumentation({
                    propagateTraceHeaderCorsUrls: [
                        /localhost:.*/,
                        /nutrition-api.*/
                    ]
                }),
                new FetchInstrumentation({
                    propagateTraceHeaderCorsUrls: [
                        /localhost:.*/,
                        /nutrition-api.*/
                    ]
                }),
                new WebVitalsInstrumentation()
            ]
        });
    }

    public trackCustomMetric(name: string, value: number, attributes: Record<string, string> = {}) {
        const span = this.tracerProvider
            .getTracer('nutrition-metrics')
            .startSpan(`metric.${name}`);
        
        span.setAttribute('metric.value', value);
        Object.entries(attributes).forEach(([key, value]) => {
            span.setAttribute(key, value);
        });
        
        span.end();
    }

    public trackMealInteraction(mealId: string, interactionType: string, duration: number) {
        const span = this.tracerProvider
            .getTracer('nutrition-interactions')
            .startSpan('meal.interaction');
        
        span.setAttribute('meal.id', mealId);
        span.setAttribute('interaction.type', interactionType);
        span.setAttribute('interaction.duration_ms', duration);
        
        span.end();
    }

    public trackGoalProgress(goalId: string, progress: number, target: number) {
        const span = this.tracerProvider
            .getTracer('nutrition-goals')
            .startSpan('goal.progress');
        
        span.setAttribute('goal.id', goalId);
        span.setAttribute('goal.progress', progress);
        span.setAttribute('goal.target', target);
        span.setAttribute('goal.completion_rate', (progress / target) * 100);
        
        span.end();
    }

    public trackUIPerformance(componentName: string, renderTime: number) {
        const span = this.tracerProvider
            .getTracer('nutrition-ui')
            .startSpan('ui.render');
        
        span.setAttribute('component.name', componentName);
        span.setAttribute('render.duration_ms', renderTime);
        
        span.end();
    }

    public trackUserJourney(journeyName: string, steps: string[], duration: number) {
        const span = this.tracerProvider
            .getTracer('nutrition-journeys')
            .startSpan('user.journey');
        
        span.setAttribute('journey.name', journeyName);
        span.setAttribute('journey.steps', steps.join(','));
        span.setAttribute('journey.duration_ms', duration);
        span.setAttribute('journey.step_count', steps.length);
        
        span.end();
    }
}
