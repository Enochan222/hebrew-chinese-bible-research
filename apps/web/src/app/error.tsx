"use client";

export default function ErrorPage() {
  return (
    <main className="page-shell failure-shell">
      <section className="failure-card">
        <p className="eyebrow">P1-VS-001 fixture shell</p>
        <h1>Unexpected rendering failure</h1>
        <p>The fixture shell failed without exposing implementation details.</p>
        <code>DATA_TEMPORARILY_UNAVAILABLE</code>
      </section>
    </main>
  );
}
