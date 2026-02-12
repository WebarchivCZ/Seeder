(function () {
    "use strict";

    var DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024;

    function parseJSONResponse(response) {
        return response.text().then(function (text) {
            if (!text) {
                return {};
            }
            try {
                return JSON.parse(text);
            } catch (error) {
                return {};
            }
        });
    }

    function getUploadErrorMessage(payload, fallback) {
        if (payload && payload.detail) {
            return payload.detail;
        }
        if (payload && payload.offset !== undefined) {
            return fallback + " (offset " + payload.offset + ")";
        }
        return fallback;
    }

    function formatProgress(current, total) {
        if (!total) {
            return 0;
        }
        return Math.floor((current / total) * 100);
    }

    document.addEventListener("DOMContentLoaded", function () {
        var form = document.getElementById("internal-tc-edit-form");
        if (!form) {
            return;
        }

        var uploadUrl = form.getAttribute("data-chunk-upload-url");
        var completeUrl = form.getAttribute("data-chunk-complete-url");
        var chunkSize = Number(form.getAttribute("data-chunk-size")) || DEFAULT_CHUNK_SIZE;

        var fileInput = document.getElementById("id_custom_seeds_chunk_file");
        var uploadIdInput = document.getElementById("id_custom_seeds_upload_id");
        var submitButton = document.getElementById("internal-tc-edit-submit");
        var progressBar = document.getElementById("custom-seeds-upload-progress");
        var statusElement = document.getElementById("custom-seeds-upload-status");
        var csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");

        if (!uploadUrl || !completeUrl || !fileInput || !uploadIdInput ||
                !submitButton || !progressBar || !statusElement || !csrfInput) {
            return;
        }

        var defaultStatusText = statusElement.getAttribute("data-default-text") || "";
        var csrfToken = csrfInput.value;
        var state = {
            hasSelectedFile: false,
            uploading: false,
            completed: false,
            token: 0
        };

        function setStatus(text, isError) {
            statusElement.textContent = text;
            statusElement.classList.toggle("text-danger", Boolean(isError));
            statusElement.classList.toggle("text-success", !isError && state.completed);
        }

        function setProgress(percent) {
            var value = Math.max(0, Math.min(100, percent));
            progressBar.style.width = value + "%";
            progressBar.setAttribute("aria-valuenow", String(value));
            progressBar.textContent = value + "%";
        }

        function syncSubmitLock() {
            submitButton.disabled = state.uploading || (state.hasSelectedFile && !state.completed);
        }

        function resetUploadFields() {
            uploadIdInput.value = "";
            state.completed = false;
            setProgress(0);
        }

        async function uploadFileInChunks(file, token) {
            var uploadId = "";
            var offset = 0;
            var spark = new SparkMD5.ArrayBuffer();

            state.uploading = true;
            state.completed = false;
            syncSubmitLock();
            setStatus("Uploading custom seeds...", false);
            setProgress(0);

            try {
                while (offset < file.size) {
                    if (token !== state.token) {
                        return;
                    }

                    var end = Math.min(offset + chunkSize, file.size);
                    var chunk = file.slice(offset, end);
                    var chunkBuffer = await chunk.arrayBuffer();
                    spark.append(chunkBuffer);

                    var chunkData = new FormData();
                    chunkData.append("file", chunk, file.name);
                    chunkData.append("filename", file.name);
                    chunkData.append("offset", String(offset));
                    if (uploadId) {
                        chunkData.append("upload_id", uploadId);
                    }

                    var chunkResponse = await fetch(uploadUrl, {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "Content-Range": "bytes " + offset + "-" + (end - 1) + "/" + file.size
                        },
                        body: chunkData
                    });
                    var chunkPayload = await parseJSONResponse(chunkResponse);

                    if (!chunkResponse.ok) {
                        throw new Error(getUploadErrorMessage(
                            chunkPayload, "Chunk upload failed"));
                    }

                    uploadId = chunkPayload.upload_id;
                    offset = chunkPayload.offset;
                    setProgress(formatProgress(offset, file.size));
                }

                if (!uploadId) {
                    throw new Error("Upload did not return upload id");
                }

                setStatus("Finalizing upload checksum...", false);
                var completeData = new URLSearchParams();
                completeData.append("upload_id", uploadId);
                completeData.append("md5", spark.end());

                var completeResponse = await fetch(completeUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                    },
                    body: completeData.toString()
                });
                var completePayload = await parseJSONResponse(completeResponse);
                if (!completeResponse.ok) {
                    throw new Error(getUploadErrorMessage(
                        completePayload, "Upload completion failed"));
                }

                if (token !== state.token) {
                    return;
                }

                uploadIdInput.value = uploadId;
                state.completed = true;
                setProgress(100);
                setStatus("Upload completed. You can submit the form.", false);
            } catch (error) {
                if (token !== state.token) {
                    return;
                }
                resetUploadFields();
                setStatus(error.message || "Upload failed", true);
            } finally {
                if (token === state.token) {
                    state.uploading = false;
                    syncSubmitLock();
                }
            }
        }

        fileInput.addEventListener("change", function () {
            state.token += 1;
            resetUploadFields();

            var file = fileInput.files[0];
            if (!file) {
                state.hasSelectedFile = false;
                state.uploading = false;
                setStatus(defaultStatusText, false);
                syncSubmitLock();
                return;
            }

            state.hasSelectedFile = true;
            if (!file.name.toLowerCase().endsWith(".txt")) {
                setStatus("Only .txt files are allowed.", true);
                syncSubmitLock();
                return;
            }

            uploadFileInChunks(file, state.token);
        });

        form.addEventListener("submit", function (event) {
            if (state.uploading) {
                event.preventDefault();
                setStatus("Please wait for the upload to finish before submitting.", true);
                return;
            }
            if (state.hasSelectedFile && !uploadIdInput.value) {
                event.preventDefault();
                setStatus("Please complete file upload before submitting.", true);
            }
        });

        syncSubmitLock();
    });
})();
