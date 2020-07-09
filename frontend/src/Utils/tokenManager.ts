import client from "Api/client";

class TokenManager {
  private tokenKey: string = "auth-token";
  token: string | null;

  constructor() {
    this.token = localStorage.getItem("auth-token");
    if (this.token)
      client.defaults.headers.common["Authorization"] = `Token ${this.token}`;
  }

  get isAuthenticated(): boolean {
    return !!this.token;
  }

  setToken(newToken: string) {
    this.token = newToken;
    localStorage.setItem(this.tokenKey, this.token);
    client.defaults.headers.common["Authorization"] = `Token ${this.token}`;
  }

  removeToken() {
    this.token = null;
    localStorage.removeItem(this.tokenKey);
    client.defaults.headers.common["Authorization"] = "";
  }
}

const tokenManager = new TokenManager();
export default tokenManager;
