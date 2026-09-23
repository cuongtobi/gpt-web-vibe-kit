import { rotateSessionCookie } from "../../../lib/session";

export async function POST() {
  return Response.json(rotateSessionCookie("expired-session"));
}
