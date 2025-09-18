// wer das liest ist wahrscheinlich Jakob lol
// Achtung dieser Code ist zum größten Teil AI generiert und kann Fehler enthalten.
const scriptName = window.SCRIPT_NAME || '';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function hideElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.add("hidden");
    element.classList.remove("visible-block", "visible-flex");
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
}
  else if (mode === "flex") {
    if (element) {
      element.classList.add("visible-flex");
      element.classList.remove("hidden");
    } else {
      console.error(`Element with ID ${elementId} not found.`);
    }
  }
}

// Event Listeners für die Toggle-Buttons hinzufügen
document.addEventListener('DOMContentLoaded', function() {
  const searchRadio = document.getElementById('search');
  const boardRadio = document.getElementById('board');
  
  if (searchRadio) {
    searchRadio.addEventListener('change', function() {
      if (this.checked) {
        showSearch(event);
      }
    });
  }
  
  if (boardRadio) {
    boardRadio.addEventListener('change', function() {
      if (this.checked) {
        showDashboard(event);
      }
    });
  }
  
  // Standardmäßig Board anzeigen beim Laden der Seite
  showDashboard({ preventDefault: () => {} });
  // Board Radio Button als checked setzen
  if (boardRadio) {
    boardRadio.checked = true;
  }
});

function showDashboard(event) {
  event.preventDefault(); // Prevent the default form submission behavior
  // Hide Search and Search Results
  hideElement("searchContainerAPI");
  hideElement("searchResults");

  // Show Dashboard and Profile Selector
  showElement("dashboard", "block");
  showElement("searchContainerDashboard", "flex");
}

function showSearch(event) {
  event.preventDefault(); // Prevent the default form submission behavior
  //Hide Dashboard und Profile Selector
  hideElement("dashboard");
  hideElement("searchContainerDashboard");
  // Show Search and Search Results
  showElement("searchContainerAPI", "flex");
  showElement("searchResults", "flex");
}
// Function to handle the search button click
function searchMovie(event) {
  event.preventDefault(); // Prevent the default form submission behavior

  // Check if the input field exists
  if (!event.target.movieSearchInput) {
    alert("Search input field not found.");
    return;
  }

  var searchTerm = document.getElementById("movieSearchInput").value.trim();

  // Validate the search term
  if (searchTerm.trim() === "") {
    alert("Please enter a movie name.");
    return;
  }

  console.log("Searching for movie:", searchTerm);

  //getAPIData(searchTerm);
  const url = `https://imdb.iamidiotareyoutoo.com/justwatch?q=${encodeURIComponent(
    searchTerm
  )}&L=de_DE`;
  console.log("Fetching data from URL:", url);
  displayMovieSearchResults(url);
}

// Function to fetch movie data from the API and display results
function displayMovieSearchResults(url) {
  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json(); // Automatisches JSON-Parsing
    })
    .then((data) => {
      console.log("JSON Data:", data);

      // Show the API results in the console
      if (data && data.description) {
        console.log("Movies found:", data.description.length);
        // Durchlaufen der Filme
        data.description.forEach((movie, index) => {
          console.log(`Film ${index + 1}:`, {
            title: movie.title,
            runtime: movie.runtime,
            poster: movie.photo_url[0],
            imdb_URL: movie.url,
          });
        });
        // Filme in die UI anzeigen

        let movies = data.description;
        let resultsContainer = document.getElementById("searchResults");
        //clear container content
        resultsContainer.innerHTML = "";

        if (movies && movies.length > 0) {
          movies.forEach((movie) => {
            const movieElement = document.createElement("div");
            const usingDefaultImage = !(movie.photo_url && movie.photo_url[0] != undefined);
            movieElement.className = "movieItem";

            // Hintergrundbild setzen, falls nicht vorhanden, Standardbild verwenden
            if (movie.photo_url && movie.photo_url[0] != undefined) {
              movieElement.style.backgroundImage = `url('${movie.photo_url[0]}')`;
            } else {
              movieElement.style.backgroundImage = `url('${scriptName}/static/movies/ui/default_poster.png')`;
            }
            movieElement.style.backgroundSize = "cover";
            movieElement.style.backgroundPosition = "center";
            movieElement.style.backgroundRepeat = "no-repeat";

            movieElement.innerHTML = `
              <div class="movie-overlay">
                ${usingDefaultImage ? `<h3 class="movieTitleNoImg">${movie.title || "Unbekannter Titel"}</h3>` : ''}
                <h3 class="movieTitle">${movie.title || "Unbekannter Titel"}</h3>
                <h5 class="movieRuntime">${movie.runtime || "--"} min</h5>
                <div class="button-container-horizontal">
                  <a href="${movie.url || "#"}" target="_blank">
                    <button>Mehr</button>
                  </a>
                  <form method="post" action="${scriptName}/movies/vote_search/${movie.id}/${encodeURIComponent(movie.title)}/">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                    <button type="submit">Vote</button>
                  </form>
                </div>
              </div>
            </div>
            `;

            // Optional: Button zum Suchen auf werstreamt.es
            // <a href="https://www.werstreamt.es/filme-serien/?q=${encodeURIComponent(movie.imdbId || "")}&action_results=suchen" target="_blank">
            // <button>Wo?</button></a>
            //oder eigene Seite mit infos
            resultsContainer.appendChild(movieElement);
          });
        } else {
          resultsContainer.innerHTML = "<p>Keine Filme gefunden.</p>";
        }
      } else {
        console.log("Keine Filme gefunden oder unerwartete Datenstruktur");
      }
    })
    .catch((error) => {
      console.error("Error fetching JSON data:", error);
      alert("Fehler beim Laden der Filmdaten. Bitte versuchen Sie es erneut.");
    });
}

// Combined filter function that handles both search and user filters
function filterMoviesByVoters() {
  const userCheckboxes = document.querySelectorAll('input[data-user]');
  const movieItems = document.querySelectorAll('#movieContainer .movieItem');
  const searchInput = document.getElementById('movieSearchInputDashboard');
  
  const checkedUsers = Array.from(userCheckboxes)
    .filter(cb => cb.checked)
    .map(cb => cb.dataset.user);
    
  const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';

  movieItems.forEach(movieItem => {
    // Check if movie matches search term
    const movieTitle = movieItem.getAttribute('data-title').toLowerCase();
    const matchesSearch = searchTerm === '' || movieTitle.includes(searchTerm);
    
    // Check if movie has votes from selected users
    const voters = movieItem.dataset.voters ? movieItem.dataset.voters.split('|') : [];
    const matchesUserFilter = checkedUsers.length === 0 || checkedUsers.some(user => voters.includes(user));
    
    // Show movie only if it matches both filters
    const shouldShow = matchesSearch && matchesUserFilter;
    movieItem.style.display = shouldShow ? 'block' : 'none';
  });
  
  // Check if only one movie is visible and add single-center class
  const visibleMovies = Array.from(movieItems).filter(item => item.style.display !== 'none');
  const movieContainer = document.getElementById('movieContainer');
  
  if (visibleMovies.length === 1 && movieContainer) {
    movieContainer.classList.add('single-center');
  } else if (movieContainer) {
    movieContainer.classList.remove('single-center');
  }
}

// Function to toggle user filter avatars
function toggleUserFilter(avatarElement) {
  const checkbox = avatarElement.querySelector('input[type="checkbox"]');
  const allAvatars = document.querySelectorAll('.user-avatar-filter');
  
  // Toggle checkbox state
  checkbox.checked = !checkbox.checked;
  
  // Update visual states for all avatars
  allAvatars.forEach(avatar => {
    const cb = avatar.querySelector('input[type="checkbox"]');
    if (cb.checked) {
      avatar.classList.add('selected');
      avatar.classList.remove('unselected');
    } else {
      avatar.classList.remove('selected');
      avatar.classList.add('unselected');
    }
  });
  
  // Apply filters
  filterMoviesByVoters();
}

/*
* Event listener for the search input field
* Filters items based on the search term
*/
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('movieSearchInputDashboard');
  
  if (searchInput) {
    searchInput.addEventListener('input', filterMoviesByVoters);
  }
});

// Function to handle the User Vote Filter Checkboxes
document.addEventListener('DOMContentLoaded', () => {
  const userCheckboxes = document.querySelectorAll('input[data-user]');

  userCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', filterMoviesByVoters);
  });
});