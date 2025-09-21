function openEditProfileModal() {
  // Modal anzeigen
  document.getElementById("editProfileModal").style.display = "flex";
}

// Modal schließen und Formulare zurücksetzen
function closeEditProfileModal() {
  document.getElementById("editProfileModal").style.display = "none";
  // Formulare zurücksetzen
  document.getElementById("editUsernameForm").reset();
  document.getElementById("editProfileImageForm").reset();
}

// Modal schließen wenn außerhalb geklickt wird
window.onclick = function (event) {
  const modal = document.getElementById("editProfileModal");
  if (event.target == modal) {
    closeEditProfileModal();
  }
};