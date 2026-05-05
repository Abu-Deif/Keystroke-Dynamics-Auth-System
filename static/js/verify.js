const pwdInput = document.getElementById("password");
const hiddenData = document.getElementById("keystrokesData");
const loginForm = document.getElementById("loginForm");

let pressTimes = {};
let lastReleaseTime = null;
let currentAttemptStrokes = [];

pwdInput.addEventListener("keydown", e => {
    const key = e.key;
    // لو الحرف لسه متسجلش ضغطة ليه نسجله
    if (!pressTimes[key]) {
        pressTimes[key] = performance.now();
    }
});

pwdInput.addEventListener("keyup", e => {
    const key = e.key;
    const release = performance.now();
    const press = pressTimes[key] || release;
    const dwell = release - press;
    let flight = null;

    if (lastReleaseTime !== null) {
        flight = press - lastReleaseTime;
    }
    lastReleaseTime = release;

    // بنسجل الحروف بس (مش الزراير الخاصة زي Shift)
    if (key.length === 1) {
        currentAttemptStrokes.push({
            key: key,
            press: press,
            release: release,
            dwell: dwell,
            flight: flight
        });
    }

    delete pressTimes[key];

    // التريك هنا: كل ما يكتب حرف ويتحسب، بنحدث الحقل المخفي بالداتا كـ JSON
    hiddenData.value = JSON.stringify(currentAttemptStrokes);
});

loginForm.addEventListener("submit", e => {
    if (!hiddenData.value || hiddenData.value === "[]") {
        e.preventDefault();
        alert("Security Alert: Please type your password manually. Paste is not allowed.");
    }
});