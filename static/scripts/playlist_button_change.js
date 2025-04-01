document.addEventListener('DOMContentLoaded', () => {
    const createPlaylistForm = document.getElementById("create-playlist-form");
    const createPlaylistButton= document.getElementById("create-playlist-btn");
    const createPlaylistLoadingInfo = document.getElementById("create-playlist-loading-info");
    const createPlaylistSpinner = document.getElementById("create-playlist-spinner");
    const viewPlaylistButton = document.getElementById("view-playlist-btn");

    createPlaylistForm.addEventListener("submit", function(event) {
        event.preventDefault();

        createPlaylistButton.style.display = "none";
        createPlaylistSpinner.style.display = "block";
        createPlaylistLoadingInfo.style.display = "block";

        fetch("/create-playlist", {
            method: 'POST',
            body: new FormData(createPlaylistForm),
        })
        .then(response => response.json())
        .then(data => {
            createPlaylistSpinner.style.display = "none";
            createPlaylistLoadingInfo.style.display = "none";

            if (data.message) {
                viewPlaylistButton.style.display = "block";
                viewPlaylistButton.onclick = () => window.open(data.playlist_url, "_blank")
            }
            else if (data.error) {
                createPlaylistButton.style.display = "block";
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error: ', error);
            createPlaylistSpinner.style.display = 'none';
            createPlaylistLoadingInfo.style.display = 'none';
            createPlaylistButton.style.display = 'block';
            alert("An error occured. Please try again.")
        });
    });
});