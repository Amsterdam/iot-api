import http from "k6/http";
import { check, group, sleep } from "k6";

export default function () {
  let response = http.get("http://localhost/iothings/devices/");
  let checkRes = check(response, {
    "http2 is used": (r) => r.proto === "HTTP/2.0",
    "status is 200": (r) => r.status === 200,
    "content is present": (r) => r.body.indexOf("results") !== -1,
  });
}

export let options = {
  vus: 1,
  stages: [
    { duration: "10s", target: 5 },
    { duration: "10s", target: 10 },
    { duration: "10s", target: 35 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};
