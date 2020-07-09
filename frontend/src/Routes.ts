import HomePage from "Pages/HomePage";
import LoginPage from "Pages/LoginPage";
import RegisterPage from "Pages/RegisterPage";

const routes = [
  {
    component: LoginPage,
    path: "/login",
    exact: true,
    secure: false,
  },
  {
    component: RegisterPage,
    path: "/register",
    exact: true,
    secure: false,
  },
  {
    component: HomePage,
    path: "/",
    exact: true,
  },
];

export default routes;
