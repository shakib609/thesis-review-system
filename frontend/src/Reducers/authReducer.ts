import { createSlice, Dispatch } from "@reduxjs/toolkit";

import client from "Api/client";
import tokenManager from "Utils/tokenManager";
import history from "Utils/history";

export interface IAuthState {
  loading: "idle" | "loading";
  key: string | null;
  user: IUser | null;
  error: any;
}

const initialState: IAuthState = {
  loading: "idle",
  key: null,
  user: null,
  error: null,
};

const auth = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loggingIn(state) {
      state.loading = "loading";
    },
    loginSuccess(state, action) {
      const { key, user } = action.payload;
      state.key = key;
      state.user = user;
      state.loading = "idle";
      state.error = null;
      tokenManager.setToken(key);
      history.push("/");
      // store.dispatch(
      //   addSnackbar({ message: "Logged In Successfully!", type: "success" })
      // );
    },
    loginError(state, action) {
      state.error = action.payload;
      state.loading = "idle";
      // store.dispatch(
      //   addSnackbar({ message: "Invalid Credentials!", type: "success" })
      // );
    },
    logout(state) {
      state.key = null;
      state.user = null;
      state.error = null;
      state.loading = "idle";
      tokenManager.removeToken();
      history.push("/login");
    },
  },
});

export const { loggingIn, loginSuccess, loginError, logout } = auth.actions;

export default auth.reducer;

export const login = (username: string, password: string) => (
  dispatch: Dispatch
) => {
  dispatch(loggingIn());
  return client.post("/login/", { username, password }).then(
    (response) => dispatch(loginSuccess(response.data)),
    (err) => {
      dispatch(loginError(err.response.data));
      throw err;
    }
  );
};
