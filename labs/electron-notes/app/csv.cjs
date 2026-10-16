function escapeCell(value) {
  const text = String(value ?? '');
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function toCsv(notes) {
  const rows = [['title', 'body'], ...notes.map(({ title, body }) => [title, body])];
  return rows.map(row => row.map(escapeCell).join(',')).join('\r\n') + '\r\n';
}

module.exports = { toCsv };
