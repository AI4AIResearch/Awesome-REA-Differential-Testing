document.querySelector('#export').addEventListener('click', async () => {
  const result = await window.notes.exportCsv();
  const blob = new Blob([result.content], { type: result.mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = result.filename;
  link.click();
  URL.revokeObjectURL(url);
});
