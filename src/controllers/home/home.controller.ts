import * as express from 'express';
import { Request, Response } from 'express';

import IControllerBase from 'interfaces/IControllerBase.interface';

class HomeController implements IControllerBase {
  path = '/';
  router = express.Router();

  constructor() {
    this.initRoutes();
  }

  initRoutes() {
    this.router.get('/', this.index);
  }

  index = (req: Request, res: Response) => {
    // read new albums from db
    const response = null;

    res.send('home/index', { response });
  }
}

export default HomeController;
