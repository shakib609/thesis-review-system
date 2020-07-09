import React from "react";
import { Route, Redirect } from "react-router-dom";

import tokenManager from "Utils/tokenManager";

export default function CustomRoute({ secure = true, ...routeProps }: any) {
  if (secure) {
    if (tokenManager.isAuthenticated) return <Route {...routeProps} />;
    else return <Redirect to="/login" />;
  }
  return <Route {...routeProps} />;
}
