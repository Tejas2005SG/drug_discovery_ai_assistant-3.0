import express from "express";
import { checkAuth, login, logout, signup, loginWithGoogle, signupWithGoogle, googleCallback } from "../controller/auth.controller.js";
import { protectRoute } from "../middleware/protectRoute.js";

const router = express.Router();

router.post("/signup", signup);
router.post("/login", login);
router.post("/logout", logout);

router.get("/check", protectRoute, checkAuth);

router.get("/loginwithgoogle", loginWithGoogle);
router.get("/signupwithgoogle", signupWithGoogle);
router.get("/google/callback", googleCallback);

export default router;
