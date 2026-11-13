/**
 * BrewBean Analytics System - Main JavaScript Client Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    // Automatically perform health check on page load
    checkHealth();
});

/**
 * Calls /health endpoint to verify Flask & MySQL connectivity state
 */
function checkHealth() {
    const refreshIcon = document.getElementById('refreshIcon');
    const navDbBadge = document.getElementById('navDbBadge');
    const dbStatusTitle = document.getElementById('dbStatusTitle');
    const dbStatusDetail = document.getElementById('dbStatusDetail');
    const dbStatusIcon = document.getElementById('dbStatusIcon');
    const dbHelpAlert = document.getElementById('dbHelpAlert');

    if (refreshIcon) refreshIcon.classList.add('spin');

    fetch('/health')
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            const db = data.database || {};

            if (db.connected) {
                // MySQL Connected State
                if (navDbBadge) {
                    navDbBadge.className = 'badge rounded-pill bg-success px-3 py-2';
                    navDbBadge.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> MySQL Connected';
                }
                if (dbStatusTitle) {
                    dbStatusTitle.className = 'mb-0 text-success fw-bold d-flex align-items-center gap-2';
                    dbStatusTitle.innerHTML = `Connected <span class="badge bg-success-subtle text-success border border-success rounded-pill fs-8">Ready</span>`;
                }
                if (dbStatusDetail) {
                    dbStatusDetail.textContent = `Host: ${db.host}:${db.port || 3306} | DB: ${db.database}`;
                }
                if (dbStatusIcon) {
                    dbStatusIcon.className = 'rounded-circle bg-success text-white p-3 d-flex align-items-center justify-content-center';
                }
                if (dbHelpAlert) {
                    dbHelpAlert.classList.add('d-none');
                }
            } else {
                // MySQL Disconnected State (Graceful Handled Exception)
                if (navDbBadge) {
                    navDbBadge.className = 'badge rounded-pill bg-warning text-dark px-3 py-2';
                    navDbBadge.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i> MySQL Disconnected';
                }
                if (dbStatusTitle) {
                    dbStatusTitle.className = 'mb-0 text-warning fw-bold d-flex align-items-center gap-2';
                    dbStatusTitle.innerHTML = `Disconnected <span class="badge bg-warning-subtle text-warning border border-warning rounded-pill fs-8">Not Ready</span>`;
                }
                if (dbStatusDetail) {
                    dbStatusDetail.textContent = db.error ? `Error: ${db.error}` : 'Could not connect to MySQL instance.';
                }
                if (dbStatusIcon) {
                    dbStatusIcon.className = 'rounded-circle bg-warning text-dark p-3 d-flex align-items-center justify-content-center';
                }
                if (dbHelpAlert) {
                    dbHelpAlert.classList.remove('d-none');
                }
            }
        })
        .catch(err => {
            console.error('Health check request failed:', err);
            if (navDbBadge) {
                navDbBadge.className = 'badge rounded-pill bg-danger px-3 py-2';
                navDbBadge.innerHTML = '<i class="bi bi-x-circle-fill me-1"></i> Health Check Failed';
            }
            if (dbStatusTitle) {
                dbStatusTitle.className = 'mb-0 text-danger fw-bold';
                dbStatusTitle.textContent = 'Service Unreachable';
            }
            if (dbStatusDetail) {
                dbStatusDetail.textContent = err.message;
            }
        })
        .finally(() => {
            if (refreshIcon) refreshIcon.classList.remove('spin');
        });
}
