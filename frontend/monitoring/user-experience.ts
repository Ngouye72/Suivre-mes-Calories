import { Analytics } from '@segment/analytics-next';
import { v4 as uuidv4 } from 'uuid';

export class UserExperienceMonitor {
    private static instance: UserExperienceMonitor;
    private analytics: Analytics;
    private sessionId: string;

    private constructor() {
        this.analytics = new Analytics({
            writeKey: process.env.SEGMENT_WRITE_KEY || ''
        });
        this.sessionId = uuidv4();
    }

    public static getInstance(): UserExperienceMonitor {
        if (!UserExperienceMonitor.instance) {
            UserExperienceMonitor.instance = new UserExperienceMonitor();
        }
        return UserExperienceMonitor.instance;
    }

    public trackPageView(pageName: string, properties: Record<string, any> = {}) {
        this.analytics.page(pageName, {
            ...properties,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackFeatureUsage(featureName: string, properties: Record<string, any> = {}) {
        this.analytics.track('Feature Usage', {
            feature: featureName,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString(),
            ...properties
        });
    }

    public trackUserFrustration(event: {
        type: 'error' | 'rage-click' | 'dead-click' | 'form-abandon',
        context: string,
        details?: Record<string, any>
    }) {
        this.analytics.track('User Frustration', {
            ...event,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackNutritionGoal(event: {
        goalType: string,
        targetValue: number,
        currentValue: number,
        success: boolean
    }) {
        this.analytics.track('Nutrition Goal', {
            ...event,
            progressPercentage: (event.currentValue / event.targetValue) * 100,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackMealLogging(event: {
        mealType: string,
        calories: number,
        protein: number,
        carbs: number,
        fat: number,
        duration: number
    }) {
        this.analytics.track('Meal Logging', {
            ...event,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackSearchBehavior(event: {
        query: string,
        resultCount: number,
        selectedResult?: string,
        duration: number
    }) {
        this.analytics.track('Search Behavior', {
            ...event,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackOnboarding(step: number, completed: boolean, duration: number) {
        this.analytics.track('Onboarding Progress', {
            step,
            completed,
            duration,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackEngagement(event: {
        feature: string,
        action: string,
        duration: number,
        success: boolean
    }) {
        this.analytics.track('User Engagement', {
            ...event,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public trackABTestExposure(event: {
        testName: string,
        variant: string,
        feature: string
    }) {
        this.analytics.track('AB Test Exposure', {
            ...event,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }

    public identifyUser(userId: string, traits: Record<string, any> = {}) {
        this.analytics.identify(userId, {
            ...traits,
            sessionId: this.sessionId,
            lastActivity: new Date().toISOString()
        });
    }

    public trackPerformanceMetrics(metrics: {
        pageLoadTime: number,
        ttfb: number,
        fcp: number,
        lcp: number,
        cls: number,
        fid: number
    }) {
        this.analytics.track('Performance Metrics', {
            ...metrics,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }
}
