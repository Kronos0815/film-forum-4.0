function hideElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.add("hidden");
    element.classList.remove("visible-block", "visible-flex", "visible-inline-block");
  } else {
    console.error(`Element with ID ${elementId} not found.`);
  }
}

function showElement(elementId, mode) {
  const element = document.getElementById(elementId);

  if (mode === "block") {
    if (element) {
      element.classList.add("visible-block");
      element.classList.remove("hidden");
    } else {
      console.error(`Element with ID ${elementId} not found.`);
    }
  } else if (mode === "flex") {
    if (element) {
      element.classList.add("visible-flex");
      element.classList.remove("hidden");
    } else {
      console.error(`Element with ID ${elementId} not found.`);
    }
  } else if (mode === "inline-block") {
    if (element) {
      element.classList.add("visible-inline-block");
      element.classList.remove("hidden");
    } else {
      console.error(`Element with ID ${elementId} not found.`);
    }
  }
}

function showNewUserForm() {
    hideElement("profileContainer");
    hideElement("logoutButton");

    showElement("newUserFormContainer", "block");
}

function cancelNewUserForm() {
    hideElement("newUserFormContainer");

    showElement("profileContainer", "flex");
    showElement("logoutButton", "inline-block");
}

