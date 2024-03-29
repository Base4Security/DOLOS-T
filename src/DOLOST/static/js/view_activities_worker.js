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
    // Update UI with Obsercable IPs
    updateIPs(observable_ips);
});

// Function to update the UI with unique logs
function updateUI(logs) {
    const logList = document.getElementById('logList');
    const logListModal = document.getElementById('logListModal');

    // Iterate over logs and append only new ones
    logs.forEach(log => {
        logList.innerHTML = '';
        logListModal.innerHTML = '';
        const listItem = document.createElement('p');
        listItem.textContent = log;
        listItem.classList.add('log-line');
        logList.appendChild(listItem);

        const modalListItem = listItem.cloneNode(true); // Clone the list item for modal
        logListModal.appendChild(modalListItem);
    });
}

// Function to update the UI with Obsercable IPs
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

        // Create and append the 'ip' cell
        var ipCell = document.createElement('td');
        ipCell.textContent = parsed_item.ip;
        row.appendChild(ipCell);

        // Create and append the 'timestamp' cell
        var timestampCell = document.createElement('td');
        timestampCell.textContent = parsed_item.timestamp;
        row.appendChild(timestampCell);

        // Append the row to the table body
        ObservableIpTableBody.appendChild(row);
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
