import { Router, type IRouter } from "express";
import healthRouter from "./health";
import arxivRouter from "./arxiv";

const router: IRouter = Router();

router.use(healthRouter);
router.use("/arxiv", arxivRouter);

export default router;
