import { PassageFailureView } from "@/features/passage-shell/PassageShell";

export default function NotFound() {
  return (
    <PassageFailureView
      failure={{
        code: "REFERENCE_NOT_FOUND",
        title: "Route not found",
        message: "This fixture shell exposes only the scoped P1-VS-001 passage routes.",
      }}
    />
  );
}
