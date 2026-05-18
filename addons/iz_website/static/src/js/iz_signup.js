/** @odoo-module **/
/**
 * IronZone Signup – client-side age validation & UX enhancements.
 * Runs only on /web/signup page.
 */
(function () {
    'use strict';

    if (!location.pathname.startsWith('/web/signup')) return;

    const MIN_AGE = 14;

    function calcAge(dateStr) {
        if (!dateStr) return null;
        const bd = new Date(dateStr);
        if (isNaN(bd)) return null;
        const today = new Date();
        let age = today.getFullYear() - bd.getFullYear();
        const m = today.getMonth() - bd.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < bd.getDate())) age--;
        return age;
    }

    function setMaxDate() {
        const input = document.getElementById('iz_birthdate');
        if (!input) return;
        const d = new Date();
        d.setFullYear(d.getFullYear() - MIN_AGE);
        input.max = d.toISOString().split('T')[0];
    }

    function updateAgeHint() {
        const input = document.getElementById('iz_birthdate');
        const hint = document.getElementById('iz_age_display');
        if (!input || !hint) return;
        const age = calcAge(input.value);
        if (age === null) { hint.style.display = 'none'; return; }
        if (age < MIN_AGE) {
            hint.textContent = `⛔ Debes tener al menos ${MIN_AGE} años. (Tienes ${age})`;
            hint.style.color = '#ff4f86';
            hint.style.display = 'block';
        } else {
            hint.textContent = `✅ Edad: ${age} años`;
            hint.style.color = '#52b788';
            hint.style.display = 'block';
        }
    }

    function validateOnSubmit(e) {
        const input = document.getElementById('iz_birthdate');
        if (!input || !input.value) return;
        const age = calcAge(input.value);
        if (age !== null && age < MIN_AGE) {
            e.preventDefault();
            updateAgeHint();
            input.focus();
        }
    }

    function clearError(el) {
        const next = el.nextElementSibling;
        if (next && next.classList && next.classList.contains('iz-field-error')) {
            next.remove();
        }
    }

    function showError(el, msg) {
        clearError(el);
        const err = document.createElement('div');
        err.className = 'form-text text-danger iz-field-error';
        err.textContent = msg;
        el.parentNode.appendChild(err);
    }

    function validateRequiredFields(e) {
        let ok = true;
        const selects = ['iz_gender', 'iz_fitness_goal', 'iz_experience_level'];
        selects.forEach(function (id) {
            const el = document.getElementById(id);
            if (!el) return;
            clearError(el);
            if (!el.value) {
                ok = false;
                showError(el, 'Este campo es obligatorio.');
                if (ok === false) el.focus();
            }
        });
        return ok;
    }

    document.addEventListener('DOMContentLoaded', function () {
        setMaxDate();
        const dateInput = document.getElementById('iz_birthdate');
        if (dateInput) {
            dateInput.addEventListener('change', updateAgeHint);
            dateInput.addEventListener('input', updateAgeHint);
        }
        const form = document.querySelector('form#signup_form, form[action*="signup"]');
        if (form) {
            form.addEventListener('submit', function (ev) {
                // validate required selects first
                const ok = validateRequiredFields(ev);
                if (!ok) {
                    ev.preventDefault();
                    return;
                }
                validateOnSubmit(ev);
            });
        }
    });
})();
