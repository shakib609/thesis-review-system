import axios from "axios";

const baseURLPrefix =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://trs.pythonanywhere.com";

const client = axios.create({
  baseURL: `${baseURLPrefix}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
