const date_selectors = {
	start_date: document.getElementById('start_date'),
	end_date: document.getElementById('end_date'),
};

function format_date(date) {
	const month = (date.getMonth() + 1).toString().padStart(2, '0');
	const day = date.getDate().toString().padStart(2, '0');
	const year = date.getFullYear();
	return `${year}-${month}-${day}`;
}

function format_time(time_string) {
	const date = new Date(time_string);
	return date.toLocaleString();
}

async function get_stats() {
	const today = new Date();
	const start_date = (() => {
		const value = date_selectors.start_date.value;
		if (value !== '') {
			return value;
		}
		const date = new Date(today.valueOf());
		date.setDate(date.getDate() - 7);
		return format_date(date);
	})();
	const end_date = (() => {
		const value = date_selectors.end_date.value;
		if (value !== '') {
			return value;
		}
		return format_date(today);
	})();

	const response = await fetch(
		`/api/reports/renewalstats/?format=json&start_date=${start_date}&end_date=${end_date}`
	);
	const data = await response.json();

	return data;
}

function update_auto_table(data) {
	const table = document.getElementById('auto_renewal_table');
	const tbody = table.querySelector('tbody');
	tbody.innerHTML = '';
	data.forEach((row) => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${row.hostname}</td>
			<td>${row.mac}</td>
			<td>${format_time(row.expires)}</td>
			<td>${format_time(row.changed)}</td>
		`;
		tbody.appendChild(tr);
	});
	if (data.length === 0) {
		const tr = document.createElement('tr');
		tr.innerHTML =
			'<td colspan="4">No hosts were manually renewed in the specified timeframe.</td>';
		tbody.appendChild(tr);
	}
}

function update_manual_table(data) {
	const table = document.getElementById('manual_renewal_table');
	const tbody = table.querySelector('tbody');
	tbody.innerHTML = '';
	data.forEach((row) => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${row.hostname}</td>
			<td>${row.mac}</td>
			<td>${format_time(row.expires)}</td>
			<td>${format_time(row.changed)}</td>
		`;
		tbody.appendChild(tr);
	});
	if (data.length === 0) {
		const tr = document.createElement('tr');
		tr.innerHTML =
			'<td colspan="4">No soon-to-expire hosts were manually renewed in the specified timeframe.</td>';
		tbody.appendChild(tr);
	}
}

function update_unrenewed_table(data) {
	const table = document.getElementById('unrenewed_table');
	const tbody = table.querySelector('tbody');
	tbody.innerHTML = '';
	data.forEach((row) => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${row.hostname}</td>
			<td>${row.mac}</td>
			<td>${format_time(row.expires)}</td>
			<td>${format_time(row.last_notified)}</td>
		`;
		tbody.appendChild(tr);
	});
	if (data.length === 0) {
		const tr = document.createElement('tr');
		tr.innerHTML =
			'<td colspan="4">No unrenewed hosts had notifications sent in the specified timeframe.</td>';
		tbody.appendChild(tr);
	}
}

function update_summary_table(data) {
	const auto_count_el = document.getElementById('auto_count');
	const manual_count_el = document.getElementById('manual_count');
	const unrenewed_count_el = document.getElementById('unrenewed_count');

	auto_count_el.textContent = data.auto_renewed.length;
	manual_count_el.textContent = data.notified_renewed.length;
	unrenewed_count_el.textContent = data.notified_unrenewed.length;
}

async function update_tables() {
	const stats = await get_stats();

	update_summary_table(stats);

	update_auto_table(stats.auto_renewed);
	update_manual_table(stats.notified_renewed);
	update_unrenewed_table(stats.notified_unrenewed);
}

function init() {
	const today = new Date();
	date_selectors.start_date.value = format_date(
		new Date(today.valueOf() - 7 * 24 * 60 * 60 * 1000)
	);
	date_selectors.end_date.value = format_date(today);
	document
		.getElementById('update_button')
		.addEventListener('click', update_tables);

	update_tables();
}

init();
