import { ApplicationInsights } from '@microsoft/applicationinsights-web';
import { environment } from '@/environments/environment';

let appInsights: ApplicationInsights | null = null;

function loggingEnabled(): boolean {
  return true;
}

function label(name: string): string {
  return `${environment.title} - ${name}`;
}

function init(): ApplicationInsights | null {
  if (!loggingEnabled()) {
    return null;
  }
  if (!appInsights) {
    appInsights = new ApplicationInsights({
      config: {
        instrumentationKey: environment.azure.applicationInsights,
        enableAutoRouteTracking: false,
      },
    });
    appInsights.loadAppInsights();
    appInsights.addTelemetryInitializer((envelope) => {
      if (envelope.tags) {
        envelope.tags['ai.cloud.role'] = environment.title;
      }
    });
    appInsights.trackEvent({ name: label('app started') });
  }
  return appInsights;
}

export const logger = {
  init,

  trackPageView(name: string, uri: string) {
    init()?.trackPageView({ name, uri });
  },

  logEvent(name: string, props?: Record<string, unknown>) {
    const ai = init();
    if (ai) {
      const text = label(name);
      console.log(text, props);
      ai.trackEvent({ name: text, properties: props });
    }
  },

  logEventObject(name: string, item: unknown) {
    const ai = init();
    if (ai) {
      const text = label(name);
      const json = JSON.stringify(item);
      console.log(text, item);
      ai.trackEvent({ name: text, properties: { json } });
    }
  },
};
