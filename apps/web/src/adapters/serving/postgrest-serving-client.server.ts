import "server-only";

export class PostgrestServingClient {
  constructor(
    private readonly baseUrl: string,
    private readonly apiKey?: string,
  ) {}

  private headers(extra?: HeadersInit): HeadersInit {
    const headers: Record<string, string> = {
      Accept: "application/json",
      "Content-Type": "application/json",
    };
    if (this.apiKey) {
      headers.apikey = this.apiKey;
      headers.Authorization = `Bearer ${this.apiKey}`;
    }
    return { ...headers, ...(extra ?? {}) };
  }

  async json<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl.replace(/\/$/, "")}${path}`, {
      ...init,
      headers: this.headers(init?.headers),
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`Serving API request failed (${response.status}) for ${path}`);
    }
    return (await response.json()) as T;
  }
}
