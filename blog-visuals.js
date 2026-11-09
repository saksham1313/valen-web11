/* Arithmetic-only reading aids; no storage, requests, or physiological model. */
(function () {
    'use strict';
    function timeGap(start, end) {
        const valid = /^(?:[01]\d|2[0-3]):[0-5]\d$/;
        if (!valid.test(start) || !valid.test(end)) return null;
        const toMinutes = value => Number(value.slice(0, 2)) * 60 + Number(value.slice(3));
        return (toMinutes(end) - toMinutes(start) + 1440) % 1440;
    }
    function caffeineTotal(perServing, servings, other) {
        const values = [perServing, servings, other];
        if (values.some(value => !Number.isFinite(value) || value < 0)) return null;
        const total = perServing * servings + other;
        return Number.isFinite(total) ? total : null;
    }
    function tempoTotal(lower, lift, pause) {
        if ([lower, lift, pause].some(value => !Number.isFinite(value) || value < 0)) return null;
        const total = lower + lift + pause;
        return total > 0 && Number.isFinite(total) ? total : null;
    }
    if (typeof module === 'object' && module.exports) module.exports = { timeGap, caffeineTotal, tempoTotal };
    if (typeof document === 'undefined') return;
    const number = input => input.value.trim() === '' || !input.validity.valid ? NaN : Number(input.value);
    const format = value => new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(value);
    const timing = document.getElementById('caffeine-gap');
    if (timing) {
        timing.querySelectorAll('input').forEach(input => { input.disabled = false; });
        const drink = document.getElementById('caffeine-time');
        const bed = document.getElementById('bed-time');
        const result = document.getElementById('gap-result');
        const fill = document.getElementById('gap-fill');
        function updateTiming() {
            const gap = timeGap(drink.value, bed.value);
            result.textContent = gap === null ? 'Choose both times.' : gap === 0 ? 'Same clock time: 0 hours.' : Math.floor(gap / 60) + 'h ' + (gap % 60) + 'm until bedtime';
            fill.style.width = gap === null ? '0%' : (gap / 1440 * 100) + '%';
        }
        timing.addEventListener('input', updateTiming);
        updateTiming();
    }
    const dose = document.getElementById('caffeine-label-math');
    if (dose) {
        dose.querySelectorAll('input').forEach(input => { input.disabled = false; });
        const per = document.getElementById('caffeine-per-serving');
        const servings = document.getElementById('caffeine-servings');
        const other = document.getElementById('caffeine-other');
        function updateDose() {
            const total = caffeineTotal(number(per), number(servings), number(other));
            document.getElementById('caffeine-total').textContent = total === null ? 'Check the amounts.' : format(total) + ' mg total';
            document.getElementById('caffeine-equation').textContent = total === null ? 'Use nonnegative numbers.' : format(number(per)) + ' × ' + format(number(servings)) + ' + ' + format(number(other)) + ' =';
        }
        dose.addEventListener('input', updateDose);
        updateDose();
    }
    const tempo = document.getElementById('rep-tempo');
    if (tempo) {
        tempo.querySelectorAll('input').forEach(input => { input.disabled = false; });
        const inputs = ['tempo-lower', 'tempo-lift', 'tempo-pause'].map(id => document.getElementById(id));
        const bars = ['tempo-lower-bar', 'tempo-lift-bar', 'tempo-pause-bar'].map(id => document.getElementById(id));
        function updateTempo() {
            const values = inputs.map(number);
            const total = tempoTotal(...values);
            document.getElementById('tempo-result').textContent = total === null ? 'Enter times with a positive total.' : format(total) + ' seconds per rep';
            bars.forEach((bar, i) => {
                bar.style.width = total === null ? '0%' : (values[i] / total * 100) + '%';
                bar.textContent = total !== null && values[i] / total >= .15 ? format(values[i]) + 's' : '';
            });
        }
        tempo.addEventListener('input', updateTempo);
        updateTempo();
    }
}());
