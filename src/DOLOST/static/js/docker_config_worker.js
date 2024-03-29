document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('configType').addEventListener('change', function() {
        var configType = this.value;
        var configFields = document.getElementById('configFields');
        configFields.innerHTML = ''; // Clear previous fields

        if (configType === 'env') {
            // No additional fields needed for environment variables
        } else if (configType === 'socket') {
            configFields.innerHTML = `
                <div class="mb-3">
                    <label for="socketPath" class="form-label">Socket Path:</label>
                    <input type="text" id="socketPath" class="form-control">
                </div>`;
        } else if (configType === 'tcp') {
            configFields.innerHTML = `
                <div class="mb-3">
                    <label for="tcpHost" class="form-label">TCP Host:</label>
                    <input type="text" id="tcpHost" class="form-control">
                </div>
                <div class="mb-3">
                    <label for="tcpPort" class="form-label">TCP Port:</label>
                    <input type="text" id="tcpPort" class="form-control">
                </div>`;
        } else if (configType === 'tcp_ssl') {
            configFields.innerHTML = `
                <div class="mb-3">
                    <label for="sslHost" class="form-label">SSL Host:</label>
                    <input type="text" id="sslHost" class="form-control">
                </div>
                <div class="mb-3">
                    <label for="sslPort" class="form-label">SSL Port:</label>
                    <input type="text" id="sslPort" class="form-control">
                </div>
                <div class="mb-3">
                    <label for="sslCaFile" class="form-label">CA Cert File:</label>
                    <input type="file" accept=".pem,.key,.crt,application/x-pem-file,application/x-x509-ca-cert" id="sslCaFile" class="form-control">
                </div>
                <div class="mb-3">
                    <label for="sslCertFile" class="form-label">SSL Certificate:</label>
                    <input type="file" accept=".pem,.key,.crt,application/x-pem-file,application/x-x509-ca-cert" id="sslCertFile" class="form-control">
                </div>
                <div class="mb-3">
                    <label for="sslKeyFile" class="form-label">SSL Key:</label>
                    <input type="file" accept=".pem,.key,.crt,application/x-pem-file,application/x-x509-ca-cert" id="sslKeyFile" class="form-control">
                </div>`;
        }
    });

    try {
        // Get the select element for configuration type
        var configTypeSelect = document.getElementById('configType');

        // Set the value of the select element based on Docker configuration
        if (dockerConfig.from_env) {
            configTypeSelect.value = 'env';
        }
        else if (dockerConfig.tcp) {
            configTypeSelect.value = 'tcp';
        }
        else if (dockerConfig.tcp_ssl) {
            configTypeSelect.value = 'tcp_ssl';
        }
        else if (dockerConfig.socket) {
            configTypeSelect.value = 'socket';
        }

        // Trigger change event to populate fields based on selected type
        configTypeSelect.dispatchEvent(new Event('change'));

        // Populate additional fields based on the selected type
        if (dockerConfig.tcp) {
            var tcpHostPort = dockerConfig.tcp.split('://')[1].split(':');
            document.getElementById('tcpHost').value = tcpHostPort[0];
            document.getElementById('tcpPort').value = tcpHostPort[1];
        }
        else if (dockerConfig.tcp_ssl) {
            document.getElementById('sslHost').value = dockerConfig.tcp_ssl.host;
            document.getElementById('sslPort').value = dockerConfig.tcp_ssl.port;
        }
        else if (dockerConfig.socket) {
                document.getElementById('socketPath').value = dockerConfig.socket;
            }
        } 
    catch (error) {
            console.error('Error:', error);
    }
    document.getElementById('configureButton').addEventListener('click', async function() {
        var configType = document.getElementById('configType').value;
        var config = {};

        if (configType === 'env') {
            // No additional configuration needed for environment variables
        } else if (configType === 'socket') {
            var socketPath = document.getElementById('socketPath').value.trim();
            if (!isValidSocketPath(socketPath)) {
                showAlert('Please enter valid socket location.');
                return;
            }
            config.socketPath = socketPath;
        } else if (configType === 'tcp') {
            var tcpHost = document.getElementById('tcpHost').value.trim();
            var tcpPort = document.getElementById('tcpPort').value.trim();
            if (!isValidHost(tcpHost) || !isValidPort(tcpPort)) {
                showAlert('Please enter valid host and port.');
                return;
            }
            config.host = tcpHost;
            config.port = parseInt(tcpPort);
        } else if (configType === 'tcp_ssl') {
            var sslHost = document.getElementById('sslHost').value.trim();
            var sslPort = document.getElementById('sslPort').value.trim();
            var sslCertFile = document.getElementById('sslCertFile').files[0];
            var sslKeyFile = document.getElementById('sslKeyFile').files[0];
            var sslcaFile = document.getElementById('sslCaFile').files[0];
            // Validate SSL files
            const isValidSSL = await isValidSSLFiles(sslCertFile, sslKeyFile, sslcaFile);
            if (!isValidHost(sslHost) || !isValidPort(sslPort) || !isValidSSL) {
                showAlert('Please enter valid host, port, SSL certificate, SSL CA, and key files.');
                return;
            }
            config.host = sslHost;
            config.port = parseInt(sslPort);
            config.sslCert = await readFileContent(sslCertFile);
            config.sslKey = await readFileContent(sslKeyFile);
            config.sslCa = await readFileContent(sslcaFile);
        }
        config.type = configType;

        initializeDockerClient(config);
    });

    async function readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(event) {
                resolve(event.target.result);
            };
            reader.onerror = function(event) {
                reject(event.target.error);
            };
            reader.readAsText(file);
        });
    }

    function showAlert(message) {
        // Create alert element
        var alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', 'alert-danger', 'mt-3');
        alertDiv.textContent = message;

        // Append alert to the container
        var container = document.getElementById('content');
        container.insertBefore(alertDiv, container.firstChild);

        // Remove alert after 5 seconds
        setTimeout(function() {
            container.removeChild(alertDiv);
        }, 5000);
    }

    // Function to validate host
    function isValidHost(host) {
        // Regular expression for valid hostname or IP address
        var hostRegex = /^(?:(?:(?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.){1,2}(?!-)[a-zA-Z]{2,}\.?|(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$)/;
        return hostRegex.test(host);
    }

    // Function to validate port
    function isValidPort(port) {
        var portNumber = parseInt(port);
        return !isNaN(portNumber) && portNumber > 0 && portNumber <= 65535;
    }

    // Function to validate socket path
    function isValidSocketPath(socketPath) {
        // Check if the socket path matches the regular expression
        var socketRegex = /^(unix|udp|tcp):\/\/(?:\/\w+)*\/\w+(\.\w+)*$/;
        return socketRegex.test(socketPath);
    }

    // Function to validate SSL certificate and key files
    async function isValidSSLFiles(certFile, keyFile, caFile) {
        // Check if all files are provided
        if (!certFile || !keyFile || !caFile) {
            return false;
        }

        try {
            const [certValid, keyValid, caValid] = await Promise.all([
                validateFileContent(certFile),
                validateFileContent(keyFile),
                validateFileContent(caFile)
            ]);

            // Check if all file contents are valid
            return certValid && keyValid && caValid;
        } catch (error) {
            console.error("Error reading file:", error);
            return false; // Assume files are invalid in case of error
        }
    }

    // Function to validate the content of a file
    function validateFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(event) {
                const fileContent = event.target.result;
                if (isValidSSLContent(fileContent)) {
                    resolve(true); // File content is valid
                } else {
                    resolve(false); // File content is invalid
                }
            };
            reader.onerror = function(event) {
                reject(event.target.error);
            };
            reader.readAsText(file);
        });
    }

    // Basic function to check for PEM format
    function isValidSSLContent(content) {
        // Regular expression to match PEM format
        const pemFormatRegex = /^(?:(?!-{3,}(?:BEGIN|END) (CERTIFICATE|RSA PRIVATE KEY))[\s\S])*(-{3,}BEGIN (CERTIFICATE|RSA PRIVATE KEY)(?:(?!-{3,}END (CERTIFICATE|RSA PRIVATE KEY))[\s\S])*?-{3,}END (CERTIFICATE|RSA PRIVATE KEY)-{3,})(?![\s\S]*?-{3,}BEGIN (CERTIFICATE|RSA PRIVATE KEY)[\s\S]+?-{3,}END (CERTIFICATE|RSA PRIVATE KEY)[\s\S]*?$)/;

        // Check if content matches the PEM format regex
        return pemFormatRegex.test(content);
    }

    function initializeDockerClient(config) {
    	button = document.getElementById('configureButton');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true">';
        var postData = JSON.stringify(config);

        $.ajax({
            type: "POST",
            url: modifyDockerClientUrl,
            contentType: "application/json",
            data: postData,
            success: function (response) {
                b5toast.show("success", "Config updated", response.message, 3000);
            },
            error: function (request, error) {
                b5toast.show("danger", "Error updating config", request.responseJSON.message, 5000);
            },
            complete: function () {
            	button.disabled = false;
                button.innerHTML = '<i class="bi bi-gear-wide-connected"></i> Configure Docker Client';
            }
        });
        
    }
});