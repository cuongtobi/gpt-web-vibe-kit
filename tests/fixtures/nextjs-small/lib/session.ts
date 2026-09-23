export function rotateSessionCookie(sessionId: string) {
  return { sessionId, rotated: true };
}
