export type HealthCheckResponse = {
  service: "ai-recruitment-api";
  status: "ok" | "degraded";
  database: "ok" | "unavailable";
};

