export function parseAppError(error) {
  try {
    return JSON.parse(error.message);
  } catch {
    return {
      message: "The request could not be completed.",
      details: [error.message],
    };
  }
}

export async function fetchJson(baseUrl, path, options = {}) {
  const response = await fetch(`${baseUrl.replace(/\/+$/, "")}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const details = Array.isArray(data.details)
      ? data.details.map((detail) => `${detail.field}: ${detail.message}`)
      : [];
    throw new Error(
      JSON.stringify({
        message: data.message || "Request failed.",
        details,
      })
    );
  }

  return data;
}

export function checkApiConnection(baseUrl) {
  return fetchJson(baseUrl, "/");
}

export function analyzeUrl(baseUrl, url) {
  return fetchJson(baseUrl, "/analyze/url", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function analyzeMessage(baseUrl, message) {
  return fetchJson(baseUrl, "/analyze/message", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
