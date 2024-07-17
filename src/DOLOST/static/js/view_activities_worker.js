let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
let update = false;

document.addEventListener('DOMContentLoaded', function () {
    initUpdates(true);
});

socket.on('connect', () => {
    console.log('[+] Connected to server');
});

socket.on('activity_logs', (data) => {
    const logs = data.logs;
    // Update UI with new logs
    updateUI(logs);
});

socket.on('activity_observable_ips', (data) => {
    const observable_ips = data.observable_ips;
    // Update UI with Observable IPs
    updateIPs(observable_ips);
});

socket.on('activity_observable_usage', (data) => {
    const observable_usage = data.observable_usage;
    // Update UI with Observable IPs
    updateUsage(observable_usage);
});

socket.on('activity_observable_interesting', (data) => {
    const observable_interesting = data.observable_interesting;
    // Update UI with Observable IPs
    updateInteresting(observable_interesting);
});

// Function to update the UI with unique logs
function updateUI(logs) {
    const logList = document.getElementById('logList');
    const logListModal = document.getElementById('logListModal');

    // Iterate over logs and append only new ones
    logList.innerHTML = '';
    logListModal.innerHTML = '';
    logs.forEach(log => {
        const listItem = document.createElement('p');
        listItem.textContent = log;
        listItem.classList.add('log-line');
        logList.appendChild(listItem);

        const modalListItem = listItem.cloneNode(true); // Clone the list item for modal
        logListModal.appendChild(modalListItem);
    });
}

// Function to update the UI with Observable IPs
function updateIPs(observable_ips) {

    var ObservableIpTableBody = document.getElementById('ObservableIpTable').getElementsByTagName('tbody')[0];

    // Clear the current rows
    ObservableIpTableBody.innerHTML = '';
    // Loop through each item in the data array
    observable_ips.forEach(function(item) {
        var parsed_item = JSON.parse(item);
        // Create a new row
        var row = document.createElement('tr');

        // Create and append the 'id' cell
        var idCell = document.createElement('th');
        idCell.scope = 'row';
        idCell.textContent = parsed_item.id;
        row.appendChild(idCell);

        // Create and append the 'timestamp' cell
        var timestampCell = document.createElement('td');
        timestampCell.textContent = parsed_item.timestamp.slice(0, -6);;
        row.appendChild(timestampCell);

        // Create and append the 'decoy' cell
        var decoyCell = document.createElement('td');
        decoyCell.textContent = parsed_item.decoy;
        row.appendChild(decoyCell);

        // Create and append the 'ip' cell
        var ipCell = document.createElement('td');
        ipCell.textContent = parsed_item.ip;
        row.appendChild(ipCell);

        // Append the row to the table body
        ObservableIpTableBody.appendChild(row);
    });
}

// Function to update the UI with Observable Usage
function updateUsage(observable_usage) {

    var ObservableUsageTableBody = document.getElementById('ObservableUsageTable').getElementsByTagName('tbody')[0];

    // Clear the current rows
    ObservableUsageTableBody.innerHTML = '';
    // Loop through each item in the data array
    observable_usage.forEach(function(item) {
        var parsed_item = JSON.parse(item);
        // Create a new row
        var row = document.createElement('tr');
        // Create and append the 'id' cell
        var idCell = document.createElement('th');
        idCell.scope = 'row';
        idCell.textContent = parsed_item.id;
        row.appendChild(idCell);

        // Create and append the 'decoy' cell
        var decoyCell = document.createElement('td');
        decoyCell.textContent = parsed_item.decoy;
        row.appendChild(decoyCell);

        // Create and append the 'usage' cell
        var usagepCell = document.createElement('td');
        usagepCell.style.textAlign = "center"; 
        usagepCell.textContent = parsed_item.usage;
        row.appendChild(usagepCell);

        // Append the row to the table body
        ObservableUsageTableBody.appendChild(row);
    });
}

// Function to update the UI with Observable IPs
function updateInteresting(observable_interesting) {

    var ObservableInterestingTableBody = document.getElementById('ObservableInterestingTable').getElementsByTagName('tbody')[0];

    // Clear the current rows
    ObservableInterestingTableBody.innerHTML = '';
    // Loop through each item in the data array
    observable_interesting.forEach(function(item) {
        var parsed_item = JSON.parse(item);
        // Create a new row
        var row = document.createElement('tr');

        // Create and append the 'id' cell
        var idCell = document.createElement('th');
        idCell.scope = 'row';
        idCell.textContent = parsed_item.id;
        row.appendChild(idCell);

        // Create and append the 'timestamp' cell
        var timestampCell = document.createElement('td');
        timestampCell.textContent = parsed_item.timestamp.slice(0, -6);
 
        row.appendChild(timestampCell);

        // Create and append the 'decoy' cell
        var decoyCell = document.createElement('td');
        decoyCell.style.textAlign = "center"; 
        decoyCell.textContent = parsed_item.decoy;
        row.appendChild(decoyCell);

        // Create and append the 'data' cell
        var dataCell = document.createElement('td');
        var icon = document.createElement('i');

        dataCell.style.textAlign = "center"; 
        icon.classList.add('bi', 'bi-eye',"h6");
        icon.style.fontSize = "14px";

        // button.appendChild(icon);
        dataCell.appendChild(icon)
        row.appendChild(dataCell);

        // Add onclick event handler
        row.onclick = function() {

            document.getElementById('modalObservableData').textContent = parsed_item.interesting_data;
            document.getElementById('modalObservableTimeStamp').textContent = parsed_item.timestamp;
            document.getElementById('modalObservableDecoy').textContent = parsed_item.decoy;

            // Show the modal
            $('#ObservableModal').modal('show');

            };
        row.title = "Show Observable"
        row.style.cursor = "pointer"
                
        // Append the row to the table body
        ObservableInterestingTableBody.appendChild(row);
    });
}

// Function to handle maximize button click
function toggleMaximize() {
    const terminalModal = new bootstrap.Modal(document.getElementById('terminalModal'));
    terminalModal.toggle();
}

// Event listener for the maximize button
document.querySelector('.maximize-button').addEventListener('click', toggleMaximize);

const unlinkLinkButtons = document.querySelectorAll('.link-unlink-button');
unlinkLinkButtons.forEach(function(button) {
   button.addEventListener('click', handleLinkUnlink);
});

function initUpdates(fresh=false){
    if (!fresh){
        socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    }
    socket.emit('request_activity');
    update = true;
}

function stopUpdate(){
    socket.close();
    update = false;
}

function handleLinkUnlink(){
    const unlinkLinkButtons = document.querySelectorAll('.link-unlink-button');
    if (update){
        stopUpdate();
        unlinkLinkButtons.forEach(function(button) {
            const buttonIcon = button.querySelector('i');
            buttonIcon.classList.remove('bi-toggle-on');
            buttonIcon.classList.add('bi-toggle-off');
        });
    }
    else{
        initUpdates();
        unlinkLinkButtons.forEach(function(button) {
            const buttonIcon = button.querySelector('i');
            buttonIcon.classList.remove('bi-toggle-off');
            buttonIcon.classList.add('bi-toggle-on');
        });
    }
}
