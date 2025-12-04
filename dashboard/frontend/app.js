// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Global state
let allLeads = [];
let selectedLeads = [];
let charts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadAnalytics();
    loadLeads();
});

// Event Listeners
function initializeEventListeners() {
    // Search form
    document.getElementById('searchForm').addEventListener('submit', handleSearch);

    // Filters
    document.getElementById('tierFilter').addEventListener('change', loadLeads);
    document.getElementById('statusFilter').addEventListener('change', loadLeads);
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadAnalytics();
        loadLeads();
    });

    // Bulk actions
    document.getElementById('selectAllCheckbox').addEventListener('change', handleSelectAll);
    document.getElementById('selectAllBtn').addEventListener('click', handleSelectAll);
    document.getElementById('generateScriptsBtn').addEventListener('click', handleGenerateScripts);
    document.getElementById('generateEmailsBtn').addEventListener('click', handleGenerateEmails);
    document.getElementById('exportCsvBtn').addEventListener('click', handleExportCsv);

    // Modal
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target.id === 'leadModal') closeModal();
    });
}

// Search Handler
async function handleSearch(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const industries = [];
    document.querySelectorAll('input[name="industry"]:checked').forEach(cb => {
        industries.push(cb.value);
    });

    const searchParams = {
        location: formData.get('location'),
        date_range: formData.get('dateRange'),
        industries: industries
    };

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchParams)
        });

        const data = await response.json();
        alert(`Search initiated: ${data.message}`);

        // Refresh after a delay
        setTimeout(() => {
            loadAnalytics();
            loadLeads();
        }, 2000);

    } catch (error) {
        console.error('Search error:', error);
        alert('Failed to initiate search');
    }
}

// Load Analytics
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/analytics`);
        const data = await response.json();

        if (data.status === 'success') {
            updateAnalytics(data.analytics);
        }
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

function updateAnalytics(analytics) {
    // Update stats
    document.getElementById('totalLeads').textContent = analytics.total_leads || 0;
    document.getElementById('tier1Count').textContent = analytics.by_tier?.[1] || 0;
    document.getElementById('tier2Count').textContent = analytics.by_tier?.[2] || 0;
    document.getElementById('avgScore').textContent = analytics.avg_score || 0;

    // Update charts
    updateTierChart(analytics.by_tier || {});
    updateStatusChart(analytics.by_status || {});
    updateIndustryChart(analytics.by_industry || {});
}

function updateTierChart(tierData) {
    const ctx = document.getElementById('tierChart');

    if (charts.tier) {
        charts.tier.destroy();
    }

    charts.tier = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5'],
            datasets: [{
                label: 'Leads by Tier',
                data: [
                    tierData[1] || 0,
                    tierData[2] || 0,
                    tierData[3] || 0,
                    tierData[4] || 0,
                    tierData[5] || 0
                ],
                backgroundColor: [
                    '#48bb78',
                    '#4299e1',
                    '#ed8936',
                    '#fc8181',
                    '#a0aec0'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Leads by Tier'
                }
            }
        }
    });
}

function updateStatusChart(statusData) {
    const ctx = document.getElementById('statusChart');

    if (charts.status) {
        charts.status.destroy();
    }

    const labels = Object.keys(statusData);
    const values = Object.values(statusData);

    charts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#667eea',
                    '#4299e1',
                    '#48bb78',
                    '#ed8936',
                    '#fc8181',
                    '#a0aec0'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Leads by Status'
                }
            }
        }
    });
}

function updateIndustryChart(industryData) {
    const ctx = document.getElementById('industryChart');

    if (charts.industry) {
        charts.industry.destroy();
    }

    const labels = Object.keys(industryData);
    const values = Object.values(industryData);

    charts.industry = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads by Industry',
                data: values,
                backgroundColor: '#764ba2'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Leads by Industry'
                }
            },
            indexAxis: 'y'
        }
    });
}

// Load Leads
async function loadLeads() {
    const tier = document.getElementById('tierFilter').value;
    const status = document.getElementById('statusFilter').value;

    let url = `${API_BASE}/leads?`;
    if (tier) url += `tier=${tier}&`;
    if (status) url += `status=${status}&`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === 'success') {
            allLeads = data.leads;
            renderLeadsTable(allLeads);
        }
    } catch (error) {
        console.error('Load leads error:', error);
    }
}

function renderLeadsTable(leads) {
    const tbody = document.getElementById('leadsTableBody');
    document.getElementById('leadCount').textContent = leads.length;

    if (leads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px; color: #999;">No leads found</td></tr>';
        return;
    }

    tbody.innerHTML = leads.map(lead => `
        <tr>
            <td><input type="checkbox" class="lead-checkbox" data-id="${lead.lead_id}"></td>
            <td><strong>${lead.company_name || 'Unknown'}</strong></td>
            <td>${lead.job_title || '-'}</td>
            <td>${lead.industry || '-'}</td>
            <td><strong>${lead.score || 0}</strong></td>
            <td><span class="tier-badge tier-${lead.tier}">${getTierLabel(lead.tier)}</span></td>
            <td><span class="status-badge">${lead.status || 'new'}</span></td>
            <td>${lead.location || '-'}</td>
            <td>
                <button class="btn-link" onclick="viewLeadDetail('${lead.lead_id}')">View</button>
            </td>
        </tr>
    `).join('');

    // Add checkbox listeners
    document.querySelectorAll('.lead-checkbox').forEach(cb => {
        cb.addEventListener('change', handleLeadSelection);
    });
}

function getTierLabel(tier) {
    const labels = {
        1: 'Tier 1 (Hot)',
        2: 'Tier 2 (Warm)',
        3: 'Tier 3 (Medium)',
        4: 'Tier 4 (Cold)',
        5: 'Tier 5 (DQ)'
    };
    return labels[tier] || `Tier ${tier}`;
}

// Lead Selection
function handleLeadSelection() {
    selectedLeads = Array.from(document.querySelectorAll('.lead-checkbox:checked'))
        .map(cb => cb.dataset.id);

    const hasSelection = selectedLeads.length > 0;
    document.getElementById('generateScriptsBtn').disabled = !hasSelection;
    document.getElementById('generateEmailsBtn').disabled = !hasSelection;
    document.getElementById('exportCsvBtn').disabled = !hasSelection;
}

function handleSelectAll() {
    const checkboxes = document.querySelectorAll('.lead-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');

    checkboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
    });

    handleLeadSelection();
}

// View Lead Detail
async function viewLeadDetail(leadId) {
    try {
        const response = await fetch(`${API_BASE}/leads/${leadId}`);
        const data = await response.json();

        if (data.status === 'success') {
            renderLeadDetail(data.lead);
            document.getElementById('leadModal').style.display = 'block';
        }
    } catch (error) {
        console.error('Load lead detail error:', error);
        alert('Failed to load lead details');
    }
}

function renderLeadDetail(lead) {
    const detailDiv = document.getElementById('leadDetail');

    detailDiv.innerHTML = `
        <h2>${lead.company_name || 'Unknown Company'}</h2>

        <div class="detail-section">
            <h3>Company Information</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Job Title</label>
                    <div>${lead.job_title || '-'}</div>
                </div>
                <div class="detail-item">
                    <label>Industry</label>
                    <div>${lead.company_industry || '-'}</div>
                </div>
                <div class="detail-item">
                    <label>Location</label>
                    <div>${lead.location || '-'}</div>
                </div>
                <div class="detail-item">
                    <label>Employee Count</label>
                    <div>${lead.company_size || 'Unknown'}</div>
                </div>
                <div class="detail-item">
                    <label>Score</label>
                    <div><strong>${lead.score || 0}</strong></div>
                </div>
                <div class="detail-item">
                    <label>Tier</label>
                    <div><span class="tier-badge tier-${lead.tier}">${getTierLabel(lead.tier)}</span></div>
                </div>
            </div>
        </div>

        ${lead.value_proposition ? `
        <div class="detail-section">
            <h3>Value Proposition</h3>
            <p>${lead.value_proposition}</p>
        </div>
        ` : ''}

        ${lead.call_script ? `
        <div class="detail-section">
            <h3>Call Script</h3>
            ${renderCallScript(lead.call_script)}
        </div>
        ` : ''}

        ${lead.email_template ? `
        <div class="detail-section">
            <h3>Email Template</h3>
            ${renderEmailTemplate(lead.email_template)}
        </div>
        ` : ''}

        ${lead.pain_points && lead.pain_points.length > 0 ? `
        <div class="detail-section">
            <h3>Identified Pain Points</h3>
            ${lead.pain_points.map(p => `
                <div class="script-section">
                    <h4>${p.category}</h4>
                    <p>${p.description}</p>
                    <small>Evidence: ${p.evidence}</small>
                </div>
            `).join('')}
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>Update Status</h3>
            <select id="leadStatus">
                <option value="new" ${lead.status === 'new' ? 'selected' : ''}>New</option>
                <option value="contacted" ${lead.status === 'contacted' ? 'selected' : ''}>Contacted</option>
                <option value="qualified" ${lead.status === 'qualified' ? 'selected' : ''}>Qualified</option>
                <option value="meeting_set" ${lead.status === 'meeting_set' ? 'selected' : ''}>Meeting Set</option>
                <option value="closed_won" ${lead.status === 'closed_won' ? 'selected' : ''}>Closed Won</option>
                <option value="closed_lost" ${lead.status === 'closed_lost' ? 'selected' : ''}>Closed Lost</option>
            </select>
            <textarea id="leadNotes" placeholder="Add notes..." rows="3" style="width: 100%; margin-top: 10px; padding: 10px;"></textarea>
            <button class="btn btn-primary" onclick="updateLeadStatus('${lead.lead_id}')" style="margin-top: 10px;">Save</button>
        </div>
    `;
}

function renderCallScript(script) {
    if (typeof script === 'string') return `<pre>${script}</pre>`;

    return `
        <div class="script-section">
            <h4>Intro</h4>
            <p>${script.intro}</p>
        </div>
        <div class="script-section">
            <h4>Pattern Interrupt</h4>
            <p>${script.pattern_interrupt}</p>
        </div>
        <div class="script-section">
            <h4>Diagnosis Question</h4>
            <p>${script.diagnosis_question}</p>
        </div>
        <div class="script-section">
            <h4>Value Statement</h4>
            <p>${script.value_statement}</p>
        </div>
        <div class="script-section">
            <h4>Meeting Ask</h4>
            <p>${script.meeting_ask}</p>
        </div>
    `;
}

function renderEmailTemplate(email) {
    if (typeof email === 'string') return `<pre>${email}</pre>`;

    return `
        <div class="detail-item" style="margin-bottom: 10px;">
            <label>Subject</label>
            <div>${email.subject}</div>
        </div>
        <pre>${email.body}</pre>
    `;
}

async function updateLeadStatus(leadId) {
    const status = document.getElementById('leadStatus').value;
    const notes = document.getElementById('leadNotes').value;

    try {
        const response = await fetch(`${API_BASE}/leads/${leadId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status, notes })
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('Lead updated successfully');
            closeModal();
            loadLeads();
        }
    } catch (error) {
        console.error('Update error:', error);
        alert('Failed to update lead');
    }
}

function closeModal() {
    document.getElementById('leadModal').style.display = 'none';
}

// Bulk Actions
async function handleGenerateScripts() {
    if (selectedLeads.length === 0) return;

    try {
        const response = await fetch(`${API_BASE}/bulk/scripts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_ids: selectedLeads })
        });

        const data = await response.json();
        alert(`Generated scripts for ${data.count} leads`);
        loadLeads();
    } catch (error) {
        console.error('Generate scripts error:', error);
        alert('Failed to generate scripts');
    }
}

async function handleGenerateEmails() {
    if (selectedLeads.length === 0) return;

    try {
        const response = await fetch(`${API_BASE}/bulk/emails`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_ids: selectedLeads })
        });

        const data = await response.json();
        alert(`Generated emails for ${data.count} leads`);
        loadLeads();
    } catch (error) {
        console.error('Generate emails error:', error);
        alert('Failed to generate emails');
    }
}

async function handleExportCsv() {
    const lead_ids = selectedLeads.length > 0 ? selectedLeads : null;

    try {
        const response = await fetch(`${API_BASE}/export/csv`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_ids })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Download CSV
            const blob = new Blob([data.csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export CSV');
    }
}

// Table Sorting
let sortDirection = {};

function sortTable(column) {
    sortDirection[column] = !sortDirection[column];

    const sorted = [...allLeads].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];

        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }

        if (sortDirection[column]) {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    renderLeadsTable(sorted);
}
