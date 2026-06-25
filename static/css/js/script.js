<script>

function updateProfile() {
    fetch("/api/update_profile", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: document.getElementById("username").value,
            email: document.getElementById("email").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function changePassword() {
    fetch("/api/change_password", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            current_password: document.getElementById("current_password").value,
            new_password: document.getElementById("new_password").value,
            confirm_password: document.getElementById("confirm_password").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

</script>