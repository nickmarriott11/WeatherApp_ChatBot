var map;
var marker; // marker variable
var selectedLocation = localStorage.getItem('selectedLocation'); // Get the selected location from local storage

// Function to initialize the map
function initializeMap() {
  if (selectedLocation) {
    // If a selected location is stored in local storage, initialize the map at that location
    map = L.map('map').setView([51.505, -0.09], 1); // Initialize the map with default coordinates and zoom level

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Call addMarker function with the stored location
    addMarker(selectedLocation);
  }
}

// Function to add a marker to the map
function addMarker(location) {
  if (marker) {
    map.removeLayer(marker); // Remove the old marker if it exists
  }

  var coordinates = location.split(',');
  var latitude = parseFloat(coordinates[0]);
  var longitude = parseFloat(coordinates[1]);
  marker = L.marker([latitude, longitude]).addTo(map)
    .bindPopup(location)
    .openPopup();

  map.setView([latitude, longitude], 8); // Set the map center to the selected location
}

// Function to update map location and get weather data when the form is submitted
function updateMapAndGetData() {
  var selectedLocation = document.getElementById('location').value;

  // Check if a location is selected before calling addMarker
  if (selectedLocation) {
    var locationName = document.getElementById('location').options[document.getElementById('location').selectedIndex].text;

    // Store the selected location in local storage
    localStorage.setItem('selectedLocation', selectedLocation);

    if (!map) {
      // If map is not initialized, initialize it now
      map = L.map('map').setView([51.505, -0.09], 1);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);
    }

    // Call addMarker function with the selected location and its name
    addMarker(selectedLocation);
  }

  // Submit the form to get weather data
  return true;
}

// Call initializeMap function when the page loads
initializeMap();