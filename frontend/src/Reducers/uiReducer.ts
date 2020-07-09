import { createSlice } from "@reduxjs/toolkit";
import { v4 as uuid4 } from "uuid";

export interface IUIState {
  snackbars: {
    id: string;
    message: string;
    type: "success" | "info" | "error" | "warning";
  }[];
}

const initialState: IUIState = {
  snackbars: [],
};

const ui = createSlice({
  name: "ui",
  initialState,
  reducers: {
    addSnackbar(state, action) {
      const { message, type } = action.payload;
      state.snackbars.push({ id: uuid4(), message, type });
    },
    removeSnackbar(state, action) {
      const snackbarIndex = state.snackbars.findIndex(
        (sb) => sb.id === action.payload
      );
      state.snackbars.splice(snackbarIndex, 1);
    },
  },
});

export const { addSnackbar, removeSnackbar } = ui.actions;

export default ui.reducer;
