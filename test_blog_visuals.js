// Behavioral arithmetic checks, including midnight and invalid inputs.
const assert = require('node:assert/strict');
const { timeGap, caffeineTotal, tempoTotal } = require('./blog-visuals.js');
assert.equal(timeGap('19:00', '23:00'), 240);
assert.equal(timeGap('23:00', '01:30'), 150);
assert.equal(timeGap('00:00', '00:00'), 0);
assert.equal(timeGap('12:01', '12:00'), 1439);
assert.equal(timeGap('24:00', '02:00'), null);
assert.equal(timeGap('', '02:00'), null);
assert.equal(caffeineTotal(200, 1.5, 100), 400);
assert.equal(caffeineTotal(0, 0, 0), 0);
assert.equal(caffeineTotal(200, -1, 100), null);
assert.equal(caffeineTotal(NaN, 1, 0), null);
assert.equal(tempoTotal(3, 1, 2), 6);
assert.equal(tempoTotal(.5, 1, .5), 2);
assert.equal(tempoTotal(0, 0, 0), null);
assert.equal(tempoTotal(3, -1, 0), null);
console.log('PASS: 14 arithmetic and invalid-input checks');
