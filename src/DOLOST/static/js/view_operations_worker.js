// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

document.addEventListener('DOMContentLoaded', function () {
    const doughnutOptions = {
        circumference: 180,
        rotation: -90,
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: "" // Title will be set dynamically
            }
        }
    };

    function createDoughnutChart(ctx, chart_name, labels, backgroundColor) {
    	return new Chart(ctx, {
    		type: 'doughnut',
    		data: {
    			labels: labels,
    			datasets: [{
    				label: '',
    				backgroundColor: backgroundColor,
    			}]
    		},
    		options: {
    			...doughnutOptions,
    			plugins:{
    				title: {
    					display: true,
    					text: `${chart_name} - ${labels[0]} vs ${labels[1]}`
    				}
    			}
    		}
    	});
    }

	const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    let intervalTimer;
    var cpuUsageChart, storageUsedChart, networkActivityChart;

    // Function to handle click event on the "Show stats" button
    function handleShowStats(event) {
        var statsContainer = document.getElementById('stats-container');
        statsContainer.classList.remove("d-none");
        statsContainer.classList.add("fade");
        setTimeout(function() {
            statsContainer.classList.add("show");
        }, 10); 
        const containerId = event.currentTarget.dataset.containerId;
        // Clear the previous interval timer if it exists
        if (intervalTimer) {
            clearInterval(intervalTimer);
        }
        // Means, first time showing stats
        else{
    	    cpuUsageChart = createDoughnutChart(document.getElementById('cpuUsageChart').getContext('2d'), 'CPU Usage', ['Used', 'Free'], ['rgb(255, 99, 132)', 'rgb(200, 200, 200)']);
		    storageUsedChart = createDoughnutChart(document.getElementById('storageUsedChart').getContext('2d'), 'Storage Used', ['Used', 'Free'], ['rgb(54, 162, 235)', 'rgb(200, 200, 200)']);
		    networkActivityChart = createDoughnutChart(document.getElementById('networkActivityChart').getContext('2d'), 'Network Activity', ['Incoming', 'Outgoing'], ['rgb(255, 206, 86)', 'rgb(75, 192, 192)']);

        }
        // Send a WebSocket request to request_data with the container_id as parameter
        socket.emit('request_data', { container_id: containerId });

        // Periodically request data every 2 seconds
        intervalTimer = setInterval(function () {
            socket.emit('request_data', { container_id: containerId });
        }, 2000);
    }

    // Add event listener to all "Show stats" buttons
    const showStatsButtons = document.querySelectorAll('.btn.btn-primary.showStatsButton');
    showStatsButtons.forEach(function(button) {
        button.addEventListener('click', handleShowStats);
    });

    // Handle WebSocket response
    socket.on('update_data', function (data) {
        updateChartData(cpuUsageChart, [data.cpu_percentage, 100 - data.cpu_percentage]);
        updateChartData(storageUsedChart, [data.memory_percentage, 100 - data.memory_percentage]);
        updateChartData(networkActivityChart, [data.network_rx, data.network_tx]);
    });

    function updateChartData(chart, newData) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
});

// Event listener for decoy form submission
document.getElementById("decoyForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    // Gather form data
    const formData = new FormData(this);
    const jsonData = Object.fromEntries(formData.entries());

    // Convert JSON data to string
    const postData = JSON.stringify(jsonData);

    // Perform AJAX request
    $.ajax({
        type: "POST",
        url: newDecoyUrl,
        contentType: "application/json",
        data: postData,
        success: function (response) {
            $("#NewDecoyModal").modal("hide");
            document.getElementById("decoyForm").reset();
            b5toast.show("success", "Decoy added successfully", "Decoy successfully stored", 3000);
            location.reload()
        },
        error: function (request, error) {
            b5toast.show("danger", "Error adding decoy", request.responseJSON.message, 5000);
        }
    });
});

// Listener for save button
document.getElementById("SaveEditOp").addEventListener("click", function () {
    var jsonData = {};

    // Iterate over accordion sections
    var accordionItems = document.querySelectorAll('.edit-op-item');
    accordionItems.forEach(function(item) {
        var header = item.querySelector('.accordion-header');
        var sectionName = header.textContent.trim();
        var sectionData = {};

        var body = item.querySelector('.accordion-body');
        var inputs = body.querySelectorAll('input, textarea');
        inputs.forEach(function(input) {
            sectionData[input.id] = input.value;
        });

        // Store section data in jsonData
        jsonData[formatSectionName(sectionName)] = sectionData;
    });

    // Send the data to the API
    editOperation(jsonData);
    // console.log(JSON.stringify(jsonData));
});

function editOperation(jsonData) {
    $.ajax({
        type: "POST",
        url: editOperationUrl,
        contentType: "application/json",
        data: JSON.stringify(jsonData),
        success: function (request) {
            var locationHeader = request.redirect;
            if (locationHeader) {
                window.location.href = window.location.origin + locationHeader;
            }
        },
        error: function (request, error) {
            b5toast.show("danger", "Error editing operation", request.responseJSON.message, 5000);
        }
    });
}

// Function to format section name
function formatSectionName(sectionName) {
    // Convert section name to lowercase and replace spaces with underscores
    return sectionName.toLowerCase().replace(/\s+/g, '_');
}


// Add event listeners to the buttons
document.addEventListener('DOMContentLoaded', function() {
    
    // Start container button
    document.querySelectorAll('.containerStartButton').forEach(function(button) {
        button.addEventListener('click', function(event) {
            var containerId = event.currentTarget.getAttribute('data-container-id');
            // Call function to start container using containerId
            startContainer(containerId, event.currentTarget);
        });
    });

    // Deploy container button
    document.querySelectorAll('.containerDeployButton').forEach(function(button) {
        button.addEventListener('click', function(event) {
            var containerHostname = event.currentTarget.getAttribute('data-container-hostname');
            // Call function to deploy container using containerId
            deployContainer(containerHostname, event.currentTarget);
        });
    });

    // Stop container button
    document.querySelectorAll('.containerStopButton').forEach(function(button) {
        button.addEventListener('click', function(event) {
            var containerId = event.currentTarget.getAttribute('data-container-id');
            // Call function to stop container using containerId
            stopContainer(containerId, event.currentTarget);
        });
    });

    // Undeploy container button
    document.querySelectorAll('.containerUndeployButton').forEach(function(button) {
        button.addEventListener('mousedown', function(event) {
            var containerId = event.currentTarget.getAttribute('data-container-id');
            var containerHostname = event.currentTarget.getAttribute('data-container-hostname');
            var currentButton = $(this);
            const duration = parseInt(500);

            // Show the tooltip and add shaking effect while button is pressed
            currentButton.tooltip('show');
            currentButton.addClass('shaking');

            // Start a timeout to Undeploy after a long press
            const timeoutId = setTimeout(() => {
                // Hide the tooltip and remove shaking effect when timeout is reached
                currentButton.tooltip('hide');
                currentButton.removeClass('shaking');
                undeployContainer(containerId, containerHostname, currentButton);
            }, duration);

            // Add event listener to cancel the timeout on mouseup
            currentButton.on('mouseup', function() {
                clearTimeout(timeoutId);
                currentButton.off('mouseup');
                // Hide the tooltip and remove shaking effect when mouse is released
                currentButton.tooltip('hide');
                currentButton.removeClass('shaking');
            });
        });
    });

        // Delete Decoy button
        document.querySelectorAll('.decoyDeleteButton').forEach(function(button) {
            button.addEventListener('mousedown', function(event) {
                var decoyHostname = event.currentTarget.getAttribute('data-container-hostname');
                var currentButton = $(this);
                const duration = parseInt(500);
    
                // Show the tooltip and add shaking effect while button is pressed
                currentButton.tooltip('show');
                currentButton.addClass('shaking');
    
                // Start a timeout to Undeploy after a long press
                const timeoutId = setTimeout(() => {
                    // Hide the tooltip and remove shaking effect when timeout is reached
                    currentButton.tooltip('hide');
                    currentButton.removeClass('shaking');
                    deleteDecoy(decoyHostname, currentButton);
                }, duration);
    
                // Add event listener to cancel the timeout on mouseup
                currentButton.on('mouseup', function() {
                    clearTimeout(timeoutId);
                    currentButton.off('mouseup');
                    // Hide the tooltip and remove shaking effect when mouse is released
                    currentButton.tooltip('hide');
                    currentButton.removeClass('shaking');
                });
            });
        });


    // Function to start container
    function startContainer(containerId, button) {
        // Disable button and show spinner
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true">';

        // Convert JSON data to string
        const postData = JSON.stringify({'containerId': containerId});

        // Perform AJAX request
        $.ajax({
            type: "POST",
            url: startContainerUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Container started", response.message, 3000);
                location.reload();
            },
            error: function (request, error) {
                b5toast.show("danger", "Error starting container", request.responseJSON.message, 5000);
            },
            complete: function () {
                // Re-enable button and remove spinner after request is complete
                button.disabled = false;
                button.innerHTML = '<i class="bi bi-play"></i>';
            }
        });
    }

    // Function to stop container
    function stopContainer(containerId, button) {
        // Disable button and show spinner
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true">';

        // Convert JSON data to string
        const postData = JSON.stringify({'containerId': containerId});

        // Perform AJAX request
        $.ajax({
            type: "POST",
            url: stopContainerUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Container stopped", response.message, 3000);
                location.reload();
            },
            error: function (request, error) {
                b5toast.show("danger", "Error stopping container", request.responseJSON.message, 5000);
            },
            complete: function () {
                // Re-enable button and remove spinner after request is complete
                button.disabled = false;
                button.innerHTML = '<i class="bi bi-stop-circle"></i>';
            }
        });
    }

    // Function to deploy container
    function deployContainer(containerHostname, button) {
        // Disable button and show spinner
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true">';

        // Convert JSON data to string
        const postData = JSON.stringify({'containerHostname': containerHostname});

        // Perform AJAX request
        $.ajax({
            type: "POST",
            url: deployContainerUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Decoy deployed successfully", response.message, 3000);
                location.reload();
            },
            error: function (request, error) {
                b5toast.show("danger", "Error deploying decoy", request.responseJSON.message, 5000);
            },
            complete: function () {
                // Re-enable button and remove spinner after request is complete
                button.disabled = false;
                button.innerHTML = '<i class="bi bi-tools"></i>';
            }
        });
    }

    // Function to undeploy container
    function undeployContainer(containerId, containerHostname, button) {
        // Disable button and show spinner
        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');

        // Convert JSON data to string
        const postData = JSON.stringify({'containerId': containerId, 'containerHostname': containerHostname});

        // Perform AJAX request
        $.ajax({
            type: "DELETE",
            url: undeployContainerUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Container removed", response.message, 3000);
                location.reload();
            },
            error: function (request, error) {
                b5toast.show("danger", "Error removing container", request.responseJSON.message, 5000);
            },
            complete: function () {
                // Re-enable button and remove spinner after request is complete
                button.prop('disabled', false).html('<i class="bi bi-trash"></i>');
            }
        });
    }

    // Function to delete decoy
    function deleteDecoy(decoyHostname, button) {
        // Disable button and show spinner
        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');

        // Convert JSON data to string
        const postData = JSON.stringify({'decoyHostname': decoyHostname});

        // Perform AJAX request
        $.ajax({
            type: "DELETE",
            url: deleteDecoyUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Container removed", response.message, 3000);
                location.reload();
            },
            error: function (request, error) {
                b5toast.show("danger", "Error removing container", request.responseJSON.message, 5000);
            },
            complete: function () {
                // Re-enable button and remove spinner after request is complete
                button.prop('disabled', false).html('<i class="bi bi-trash"></i>');
            }
        });
    }


});
