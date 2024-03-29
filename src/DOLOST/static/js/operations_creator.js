// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Listener for save button
document.getElementById("SaveNewOp").addEventListener("click", function () {
    var jsonData = {};

    // Iterate over accordion sections
    var accordionItems = document.querySelectorAll('.new-op-item');
    accordionItems.forEach(function(item) {
        var header = item.querySelector('.accordion-header');
        var sectionName = header.textContent.trim();
        var sectionData = {};

        // Skip if the section is the last one (Decoys Configuration)
        if (sectionName !== 'Decoys Configuration') {
            var body = item.querySelector('.accordion-body');
            var inputs = body.querySelectorAll('input, textarea');
            inputs.forEach(function(input) {
                sectionData[input.id] = input.value;
            });

            // Store section data in jsonData
            jsonData[formatSectionName(sectionName)] = sectionData;
        }
    });

    // Handle decoys separately
    var fileInput = document.getElementById('decoys');
    var file = fileInput.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function(event) {
            // Parse file content as JSON
            var decoys = JSON.parse(event.target.result);
            jsonData['decoys'] = decoys;
            newOperation(jsonData);
        };
        reader.readAsText(file);
    } else {
        // Send the data without the decoys
        jsonData['decoys'] = []
        newOperation(jsonData);
    }
});

function newOperation(jsonData) {
    $.ajax({
        type: "POST",
        url: newOperationUrl,
        contentType: "application/json",
        data: JSON.stringify(jsonData),
        success: function (request) {
            var locationHeader = request.redirect;
            if (locationHeader) {
                window.location.href = window.location.origin + locationHeader;
            }
        },
        error: function (request, error) {
            b5toast.show("danger", "Error adding operation", request.responseJSON.message, 5000);
        }
    });
}

// Function to format section name
function formatSectionName(sectionName) {
    // Convert section name to lowercase and replace spaces with underscores
    return sectionName.toLowerCase().replace(/\s+/g, '_');
}

// Add event listener to delete buttons
$('.delete-operation').on('mousedown', function(e) {
    const $button = $(this);
    const operationId = $button.data('operationId');
    const duration = parseInt(1000);

    // Show the tooltip amd add shaking effect while button is pressed
    $button.tooltip('show');
    $button.addClass('shaking');

    // Start a timeout to delete after a long press
    const timeoutId = setTimeout(() => {
        // Hide the tooltip and remove shaking effect when timeout is reached
        $button.tooltip('hide');
        $button.removeClass('shaking');
        deleteOperation(operationId);
    }, duration);

    // Add event listener to cancel the timeout on mouseup
    $(document).on('mouseup', function() {
        clearTimeout(timeoutId);
        $(document).off('mouseup');
        // Hide the tooltip and remove shaking effect when mouse is released
        $button.tooltip('hide');
        $button.removeClass('shaking');
    });
});

// Send request to delete operation
function deleteOperation(operationId) {
    $.ajax({
        type: 'DELETE',
        url: `${deleteOperationUrl}${operationId}`,
        success: function(result) {
            // Operation deleted successfully, remove the row from the table
            b5toast.show("success", "Operation removed!", `The operation ${operationId} has been removed.`, 3000);
            $(`#row-${operationId}`).remove();
        },
        error: function(request, error) {
            b5toast.show("danger", "Error removing operation", request.responseJSON.message, 5000);
        }
    });
}
