export default function SmartFeedbackPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Smart Feedback</h1>
      <p className="mt-1 text-sm text-muted">
        Autopsia del error: diagnóstico por sub-eje y justificación de cada
        distractor.
      </p>
      {/* TODO: vista de revisión post-examen conectada a
          GET /api/attempts/{{id}}/review */}
    </div>
  );
}
