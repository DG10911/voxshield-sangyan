export type ConnectionState =
  "CONNECTING" | "CONNECTED" | "RECONNECTING" | "DISCONNECTED" | "FAILED";
export class StreamConnection {
  private socket: WebSocket | null = null;
  private timer: ReturnType<typeof setTimeout> | undefined;
  private attempts = 0;
  private closed = false;
  constructor(
    private url: string,
    private state: (s: ConnectionState) => void,
    private message: (data: unknown) => void,
  ) {}
  connect() {
    this.closed = false;
    this.state(this.attempts ? "RECONNECTING" : "CONNECTING");
    this.socket = new WebSocket(this.url);
    this.socket.onopen = () => {
      this.attempts = 0;
      this.state("CONNECTED");
    };
    this.socket.onmessage = (e) => {
      try {
        this.message(JSON.parse(e.data));
      } catch {
        this.state("FAILED");
      }
    };
    this.socket.onerror = () => this.socket?.close();
    this.socket.onclose = () => {
      if (this.closed) return;
      if (this.attempts >= 5) {
        this.state("FAILED");
        return;
      }
      this.state("RECONNECTING");
      this.timer = setTimeout(
        () => this.connect(),
        Math.min(1000 * 2 ** this.attempts++, 16000),
      );
    };
  }
  send(data: Blob | ArrayBuffer | string) {
    if (this.socket?.readyState === WebSocket.OPEN) this.socket.send(data);
  }
  close() {
    this.closed = true;
    clearTimeout(this.timer);
    this.socket?.close();
    this.state("DISCONNECTED");
  }
}
