import express from 'express';
import { Application } from 'express';

class App {
  public app: Application;
  public port: number;

  constructor(appInit: { port: number; middleWares: any; controllers: any; }) {
    this.app = express();
    this.port = appInit.port;

    this.middlewares(appInit.middleWares);
    this.routes(appInit.controllers);
    this.assets();
    // this.template();
  }

  listen() {
    this.app.listen(this.port, () => {
      console.log(`App listening on the http://localhost:${this.port}`);
    });
  }

  private middlewares(mws: { forEach: (arg0: (mw: any) => void) => void; }) {
    mws.forEach(middleware => {
      this.app.use(middleware);
    });
  }

  private routes(controllers: { forEach: (arg0: (controller: any) => void) => void; }) {
    controllers.forEach(controller => {
      this.app.use('/', controller.router);
    });
  }

  private assets() {
    this.app.use(express.static('covers'));
    this.app.use(express.static('views'));
  }

  // TODO add server-side rendering for html
  // private template() {
  //   this.app.set('view engine', 'pug');
  // }
}

export default App;
