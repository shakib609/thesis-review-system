import React from "react";
import { Router, Switch } from "react-router-dom";
import CssBaseline from "@material-ui/core/CssBaseline";

import routes from "Routes";
import history from "Utils/history";
import CustomRoute from "Components/CustomRoute";
import DefaultLayout from "Layouts/DefaultLayout";

function App() {
  return (
    <>
      <CssBaseline />
      <Router history={history}>
        <DefaultLayout>
          <Switch>
            {routes.map((route) => (
              <CustomRoute key={route.path} {...route} />
            ))}
          </Switch>
        </DefaultLayout>
      </Router>
    </>
  );
}

export default App;
