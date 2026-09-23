import { rotateSessionCookie } from "../lib/session";

test("rotates expired session cookie", () => {
  expect(rotateSessionCookie("expired-session").rotated).toBe(true);
});
