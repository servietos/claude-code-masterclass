import { createPinia } from 'pinia';
import { createApp } from 'vue';
import App from './App.vue';
import { environment } from './environments/environment';
import router from './router';
import { logger } from './services/logger';
import { useTheme } from './services/theme';
import { useAuthStore } from './stores/auth';
import './styles/tokens.css';
import './styles/global.css';

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);
  app.use(router);
  app.config.errorHandler = () => {};

  useTheme();
  logger.init();

  if (environment.authEnabled) {
    await useAuthStore(pinia).init();
  }

  app.mount('#app');
}

bootstrap().catch((err) => console.error(err));
