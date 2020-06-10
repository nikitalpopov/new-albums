import * as bp from 'body-parser';

import App from './app';

import HomeController from './controllers/home/home.controller';
import loggerMiddleware from './middleware/logger';

const app = new App({
  port: 5000,
  controllers: [
    new HomeController()
  ],
  middleWares: [
    bp.json(),
    bp.urlencoded({ extended: true }),
    loggerMiddleware
  ]
});

app.listen();
