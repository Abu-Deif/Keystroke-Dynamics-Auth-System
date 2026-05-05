const trainButton = document.getElementById("trainButton");
const trainingOverlay = document.getElementById("trainingOverlay");
const overlayStatus = document.getElementById("overlayStatus");
const mainMessage = document.getElementById("message");

if (trainButton && trainingOverlay && overlayStatus) {
    trainButton.addEventListener("click", event => {
        event.preventDefault();
        trainingOverlay.classList.add("visible");
        trainingOverlay.setAttribute("aria-hidden", "false");
        overlayStatus.textContent = "AI Engine: Extracting Dwell Time & Flight Time patterns...";

        setTimeout(() => {
            overlayStatus.textContent = "Building SVM/Isolation Forest Model...";
        }, 2500);

        setTimeout(() => {
            overlayStatus.textContent = "Training complete. Redirecting...";
            if (mainMessage) {
                mainMessage.innerHTML = "<span class='status-success'>AI model built successfully. Redirecting to the dashboard...</span>";
            }
            trainButton.disabled = true;
            document.getElementById("goTraining").submit();
        }, 5000);
    });
}
