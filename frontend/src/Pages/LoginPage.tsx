import React, { useState } from "react";
import { useForm } from "react-hook-form";
import clsx from "clsx";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
import InputAdornment from "@material-ui/core/InputAdornment";
import InputLabel from "@material-ui/core/InputLabel";
import IconButton from "@material-ui/core/IconButton";
import OutlinedInput from "@material-ui/core/OutlinedInput";
import Visibility from "@material-ui/icons/Visibility";
import VisibilityOff from "@material-ui/icons/VisibilityOff";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import { Link } from "react-router-dom";
import { login, IAuthState } from "Reducers/authReducer";
import { useDispatch, useSelector } from "react-redux";
import { addSnackbar } from "Reducers/uiReducer";

export const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: "flex",
      flexDirection: "column",
      width: "45%",
      minWidth: 360,
      maxWidth: 420,
      justifyContent: "center",
      alignItems: "center",
      margin: "5% auto 0",
      padding: "1.5rem 0",
      backgroundColor: "white",
    },
    form: {
      display: "flex",
      flexDirection: "column",
      marginTop: 15,
      width: "100%",
      padding: "0 15px",
    },
    margin: {
      marginBottom: theme.spacing(1.5),
      "&:last-child": {
        marginBottom: 10,
      },
    },
    noMargin: {
      margin: 0,
    },
    textField: {
      width: "100%",
    },
    helperText: {
      textAlign: "right",
      margin: 0,
      marginBottom: 5,
    },
  })
);

type Inputs = {
  username: string;
  password: string;
};

export default function Login() {
  const classes = useStyles();
  const dispatch = useDispatch();
  const [showPassword, setShowPassword] = useState(false);
  const { loading, error: authError }: IAuthState = useSelector(
    (state: any) => state.auth
  );
  const { register, handleSubmit, errors } = useForm<Inputs>();

  const toggleShowPassword = () => setShowPassword(!showPassword);

  const onSubmit = ({ username, password }: Inputs) => {
    dispatch<any>(login(username, password)).then(
      () =>
        dispatch(
          addSnackbar({ message: "Logged In Successfully!", type: "success" })
        ),
      () =>
        dispatch(addSnackbar({ message: "Invalid Credentials", type: "error" }))
    );
  };

  return (
    <Paper className={classes.root}>
      <h1 className={classes.noMargin}>Login</h1>
      <form
        method="post"
        className={classes.form}
        onSubmit={handleSubmit(onSubmit)}
      >
        <FormControl
          variant="outlined"
          className={clsx(classes.margin, classes.textField)}
          error={!!(errors.username || authError)}
        >
          <InputLabel htmlFor="username-input">Username</InputLabel>
          <OutlinedInput
            required
            name="username"
            id="username-input"
            type="text"
            labelWidth={75}
            inputRef={register}
          />
        </FormControl>

        <FormControl
          variant="outlined"
          className={clsx(classes.margin, classes.textField)}
          error={!!(errors.password || authError)}
        >
          <InputLabel htmlFor="outlined-adornment-password">
            Password
          </InputLabel>
          <OutlinedInput
            name="password"
            inputRef={register}
            id="outlined-adornment-password"
            type={showPassword ? "text" : "password"}
            required
            endAdornment={
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={toggleShowPassword}
                  edge="end"
                >
                  {showPassword ? <Visibility /> : <VisibilityOff />}
                </IconButton>
              </InputAdornment>
            }
            labelWidth={70}
          />
        </FormControl>
        <FormHelperText className={classes.helperText}>
          Don't have an account? <Link to="/register">Register</Link>
        </FormHelperText>

        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={loading === "loading"}
        >
          Sign In
        </Button>
      </form>
    </Paper>
  );
}
