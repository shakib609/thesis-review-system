import React, { useState } from "react";
import clsx from "clsx";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
import InputAdornment from "@material-ui/core/InputAdornment";
import InputLabel from "@material-ui/core/InputLabel";
import IconButton from "@material-ui/core/IconButton";
import MenuItem from "@material-ui/core/MenuItem";
import OutlinedInput from "@material-ui/core/OutlinedInput";
import Select from "@material-ui/core/Select";
import Visibility from "@material-ui/icons/Visibility";
import VisibilityOff from "@material-ui/icons/VisibilityOff";
import { Link, useHistory } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";

import { useStyles } from "./LoginPage";
import client from "Api/client";
import { useDispatch } from "react-redux";
import { addSnackbar } from "Reducers/uiReducer";

type Inputs = {
  username: string;
  password: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  department: string;
  profile_picture?: string;
  cv_document?: string;
};

export default function RegisterPage() {
  const classes = useStyles();
  const dispatch = useDispatch();
  const history = useHistory();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState<"idle" | "pending">("idle");
  const [submitError, setSubmitError] = useState<any>({});
  const { register, control, handleSubmit, errors } = useForm<Inputs>({
    defaultValues: {
      department: "CSE",
    },
  });

  const toggleShowPassword = () => setShowPassword(!showPassword);

  const onSubmit = (data: Inputs, e: any) => {
    setLoading("pending");
    client
      .post("/register/", { ...data, student: {} })
      .then((response) => {
        dispatch(
          addSnackbar({ message: "Registered Successfully!", type: "success" })
        );
        history.push("/login");
        return response.data;
      })
      .catch((e) => setSubmitError(e?.response?.data || {}))
      .finally(() => setLoading("idle"));
  };

  return (
    <Paper className={classes.root}>
      <h1 className={classes.noMargin}>Register</h1>
      <form
        method="post"
        onSubmit={handleSubmit(onSubmit)}
        className={classes.form}
      >
        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!(errors.username || submitError?.username)}
        >
          <InputLabel htmlFor="username-input">Student ID</InputLabel>
          <OutlinedInput
            name="username"
            required
            id="username-input"
            type="text"
            label="Student ID"
            inputRef={register({ pattern: /^[A-Z\d]+$/, required: true })}
          />
          {errors.username && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {submitError?.username && (
            <FormHelperText>{submitError?.username}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!(errors.first_name || submitError?.first_name)}
        >
          <InputLabel htmlFor="first-name-input">First Name</InputLabel>
          <OutlinedInput
            name="first_name"
            required
            id="first-name-input"
            type="text"
            label="First Name"
            inputRef={register({ required: true })}
          />
          {errors.first_name && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {submitError?.first_name && (
            <FormHelperText>{submitError?.first_name}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!(errors.last_name || submitError?.last_name)}
        >
          <InputLabel htmlFor="last-name-input">Last Name</InputLabel>
          <OutlinedInput
            name="last_name"
            required
            id="last-name-input"
            type="text"
            label="Last Name"
            inputRef={register({ required: true })}
          />
          {errors.last_name && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {submitError?.last_name && (
            <FormHelperText>{submitError?.last_name}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!(errors.phone_number || submitError?.phone_number)}
        >
          <InputLabel htmlFor="phone-number-input">Phone Number</InputLabel>
          <OutlinedInput
            name="phone_number"
            required
            id="phone-number-input"
            type="tel"
            label="Phone Number"
            inputRef={register({ pattern: /^\d{11}$/, required: true })}
          />
          {errors.phone_number?.types?.required && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {errors.phone_number?.types?.pattern && (
            <FormHelperText>Enter an 11 digit number</FormHelperText>
          )}
          {submitError?.phone_number && (
            <FormHelperText>{submitError?.phone_number}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!(errors.email || submitError?.email)}
        >
          <InputLabel htmlFor="email-input">Email</InputLabel>
          <OutlinedInput
            name="email"
            required
            id="email-input"
            type="email"
            label="Email"
            inputRef={register({ required: true })}
          />
          {errors.email?.types?.required && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {submitError?.email && (
            <FormHelperText>{submitError?.email}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          variant="outlined"
          className={clsx(classes.margin, classes.textField)}
          error={!!submitError?.department}
        >
          <InputLabel id="demo-simple-select-outlined-label">
            Department
          </InputLabel>
          <Controller
            name="department"
            control={control}
            as={
              <Select
                labelId="demo-simple-select-outlined-label"
                id="demo-simple-select-outlined"
                label="Department"
              >
                <MenuItem value="CSE">CSE</MenuItem>
                <MenuItem value="EEE">EEE</MenuItem>
                <MenuItem value="ETE">ETE</MenuItem>
                <MenuItem value="PHM">PHM</MenuItem>
              </Select>
            }
          />
          {submitError?.department && (
            <FormHelperText>{submitError?.department}</FormHelperText>
          )}
        </FormControl>

        <FormControl
          className={clsx(classes.margin, classes.textField)}
          variant="outlined"
          error={!!submitError?.password}
        >
          <InputLabel htmlFor="outlined-adornment-password">
            Password
          </InputLabel>
          <OutlinedInput
            name="password"
            id="outlined-adornment-password"
            type={showPassword ? "text" : "password"}
            label="Password"
            required
            inputRef={register({ required: true })}
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
          />
          {errors.password?.types?.required && (
            <FormHelperText>This field is required</FormHelperText>
          )}
          {submitError?.password && (
            <FormHelperText>{submitError?.password}</FormHelperText>
          )}
        </FormControl>
        <FormHelperText className={classes.helperText}>
          Already have an account? <Link to="/login">Login</Link>
        </FormHelperText>

        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={loading === "pending"}
        >
          Sign Up
        </Button>
      </form>
    </Paper>
  );
}
