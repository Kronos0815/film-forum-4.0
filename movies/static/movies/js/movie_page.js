function openWatchedModal() {
  // Modal anzeigen
    document.getElementById("watchedModal").style.display = "flex";

  // Aktuelles Datum als Standard setzen
  document.getElementById("eventDate").value = new Date()
    .toISOString()
    .split("T")[0];
}

// Modal schließen und Formular zurücksetzen
function closeWatchedModal() {
  document.getElementById("watchedModal").style.display = "none";
  // Form zurücksetzen
  document.getElementById("watchedForm").reset();
  // Alle Attendees deselektieren
  document.querySelectorAll(".user-avatar-attendee").forEach(function (el) {
    el.classList.remove("selected");
    el.querySelector('input[type="checkbox"]').checked = false;
  });
}


function toggleAttendee(element) {
  const checkbox = element.querySelector('input[type="checkbox"]');
  checkbox.checked = !checkbox.checked;
  element.classList.toggle("selected", checkbox.checked);
}

function validateForm() {
  const checkedAttendees = document.querySelectorAll(
    'input[name="attendees"]:checked'
  );
  if (checkedAttendees.length === 0) {
    alert("Bitte wähle mindestens einen Teilnehmer aus.");
    return false;
  }
  return true;
}

function openRatingModal() {
  document.getElementById('ratingModal').style.display = 'flex';
}

function closeRatingModal() {
  document.getElementById('ratingModal').style.display = 'none';
  document.getElementById('ratingForm').reset();
  document.getElementById('movieRating').value = 5;
  updateRatingDisplay();
}

function updateRatingDisplay() {
  const value = document.getElementById('movieRating').value;
  document.getElementById('ratingDisplay').textContent = parseFloat(value).toFixed(1);
}

// Modal schließen wenn außerhalb geklickt wird
window.onclick = function (event) {
  const modal = document.getElementById("watchedModal");
  const ratingModal = document.getElementById('ratingModal');
  const voteModal = document.getElementById('voteModal');
  if (event.target == modal) {
    closeWatchedModal();
  }
  if (event.target === ratingModal) {
    ratingModal.style.display = 'none';
  }
  if (event.target === voteModal) {
    voteModal.style.display = 'none';
  }
};
