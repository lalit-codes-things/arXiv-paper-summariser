import { Router, type IRouter } from "express";
import healthRouter from "./health";
import arxivRouter from "./arxiv";
import authRouter from "./auth";

const router: IRouter = Router();

router.use(healthRouter);
router.use("/arxiv", arxivRouter);
router.use(authRouter);

export default router;
