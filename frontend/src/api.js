const BASE_URL = "http://localhost:8000/api";

function getToken() {
  return localStorage.getItem("token");
}

async function request(endpoint, options) {
  options = options || {};
  const token = getToken();
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    token ? { Authorization: "Bearer " + token } : {},
    options.headers || {}
  );

  const response = await fetch(BASE_URL + endpoint, Object.assign({}, options, { headers: headers }));

  if (!response.ok) {
    let errorData = {};
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = {};
    }
    throw new Error(errorData.detail || "Something went wrong");
  }

  return response.json();
}

export async function signup(name, email, password) {
  return request("/signup", {
    method: "POST",
    body: JSON.stringify({ name: name, email: email, password: password }),
  });
}

export async function login(email, password) {
  const data = await request("/login", {
    method: "POST",
    body: JSON.stringify({ email: email, password: password }),
  });
  localStorage.setItem("token", data.token);
  localStorage.setItem("userName", data.name);
  return data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("userName");
}

export function isLoggedIn() {
  return !!getToken();
}

export function getUserName() {
  return localStorage.getItem("userName");
}

export async function getMarketSnapshot() {
  return request("/market-snapshot", { method: "GET" });
}

export async function getMarketMovers(market) {
  market = market || "US";
  return request("/market-movers?market=" + market, { method: "GET" });
}

export async function analyzeTicker(ticker, market) {
  return request("/analyze", {
    method: "POST",
    body: JSON.stringify({ ticker: ticker, market: market }),
  });
}

export async function getPriceHistory(ticker) {
  return request("/price-history/" + ticker, { method: "GET" });
}
