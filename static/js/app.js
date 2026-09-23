function updateIstClock() {
  const node = document.getElementById("istClock");
  if (!node) return;
  node.textContent = new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  }).format(new Date()) + " IST";
}
setInterval(updateIstClock, 1000);
updateIstClock();

document.querySelectorAll(".toast").forEach((toast) => new bootstrap.Toast(toast, { delay: 3200 }).show());

document.querySelectorAll(".needs-validation").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.classList.add("was-validated");
  });
});

function fillEditForm(button) {
  const form = document.getElementById("editForm");
  if (!form) return;
  form.action = button.dataset.action;
  Object.keys(button.dataset).forEach((key) => {
    if (key === "action" || key === "bsToggle" || key === "bsTarget") return;
    const input = document.getElementById(`edit_${key}`);
    if (input) input.value = button.dataset[key];
  });
}

document.querySelectorAll(".edit-button, .schedule-edit").forEach((button) => {
  button.addEventListener("click", () => fillEditForm(button));
});
