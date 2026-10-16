const test = require('node:test');
const assert = require('node:assert/strict');
const { toCsv } = require('./csv.cjs');

test('preserves commas, quotes, and embedded newlines', () => {
  assert.equal(
    toCsv([
      { title: 'First note', body: 'Hello, reader' },
      { title: 'A "quoted" title', body: 'Line one\nLine two' },
    ]),
    'title,body\r\nFirst note,"Hello, reader"\r\n"A ""quoted"" title","Line one\nLine two"\r\n',
  );
});

test('empty collection preserves the header', () => {
  assert.equal(toCsv([]), 'title,body\r\n');
});

test('missing fields and numeric values have defined representations', () => {
  assert.equal(toCsv([{ title: 0 }]), 'title,body\r\n0,\r\n');
});
