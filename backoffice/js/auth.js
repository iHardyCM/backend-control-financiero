let token = "";

async function login() {
    const username = document.getElementById("username").value;
    const pin = document.getElementById("pin").value;

    const res = await fetch("/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, pin })
    });

    if (!res.ok) {
        document.getElementById("loginError").innerText = "Login inválido";
        return;
    }

    const data = await res.json();
    token = data.access_token;

    document.getElementById("loginBox").style.display = "none";
    document.getElementById("menuTabs").style.display = "flex";

    mostrarDashboard();
}

function logout() {
    token = "";
    location.reload();
}
