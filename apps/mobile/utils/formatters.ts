export function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}