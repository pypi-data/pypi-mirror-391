document.addEventListener("DOMContentLoaded", function () {
  const checkbox = document.querySelector("#id_use_auth");
  const userFieldRow = document
    .querySelector("#id_auth_user")
    .closest(".form-row");
  const passwordFieldRow = document
    .querySelector("#id_auth_password")
    .closest(".form-row");

  function togglePasswordField() {
    if (checkbox.checked) {
      passwordFieldRow.style.display = "";
      userFieldRow.style.display = "";
    } else {
      passwordFieldRow.style.display = "none";
      userFieldRow.style.display = "none";
    }
  }

  checkbox.addEventListener("change", togglePasswordField);
  togglePasswordField(); // Initial state
});
