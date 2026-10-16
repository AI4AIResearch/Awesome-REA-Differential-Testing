// This fixture is inspected statically; Electron is not bundled.
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { toCsv } = require('./csv.cjs');

const notes = [
  { title: 'First note', body: 'Hello, reader' },
  { title: 'A "quoted" title', body: 'Line one\nLine two' },
];

ipcMain.handle('notes:export', () => ({
  filename: 'notes.csv',
  mime: 'text/csv;charset=utf-8',
  content: toCsv(notes),
}));

app.whenReady().then(() => {
  const window = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  window.loadFile('index.html');
});
